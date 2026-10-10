"""
Invoice Automation Web GUI - combined system with PDF upload:

  /              -> Data table: ALL invoices + "Upload to MyInvois" + "Upload PDF" buttons
  /submit        -> Submit page: SUBMIT INVOICES button + stats + logs + QR links + failed list
  /upload        -> PDF upload page: file picker + process button + extracted data preview
  /qr?id=N       -> QR info page: Invoice Number, QR Code image, UUID
  /status        -> JSON: automation status
  /all-invoices  -> JSON: all invoices with status
  /submitted     -> JSON: submitted invoices
  /failed        -> JSON: failed invoices with ErrorReason
  /pdf-process   -> POST: receive PDF file, extract data, insert into DB

Run:
    python invoice_web_gui.py
Then open http://localhost:8765 in your browser.

Files in this package:
  invoice_web_gui.py  <- this file (server + automation + data table + QR viewer + PDF upload)
  check_invoices.py    <- validation layer (imported by this file)
  pdf_to_db.py         <- PDF extraction + database insertion module (imported by this file)
"""
import html
import json
import os
import re
import sys
import tempfile
import threading
import time
from datetime import datetime, date, time as dtime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

# Ensure this folder is on sys.path so we can import sibling modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pyodbc
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

import check_invoices  # validation layer (same folder)
import pdf_to_db       # PDF extraction + DB insertion (same folder)
import invoice_excel_generator  # Excel invoice generation from DB data (same folder)

# ---- Config ----
SQL_SERVER = "localhost"
SQL_DRIVER = "ODBC Driver 17 for SQL Server"
DATABASE = "CompanyInvoiceDB"       # Invoice data
PORTAL_DB = "MyInvoisPortal"        # Submission status / QR / UUID
FORM_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbzzTAgAtgrMhqCVU3r2O1jToX8hJ0GhowKMajO44cMKQJCIex5r0pYhck0yNr52XyWX/exec"
)
PORT = 8765

# ---- State ----
state = {
    "running": False,
    "logs": [],
    "total": 0,
    "done": 0,
    "success": 0,
    "failed": 0,
    "finished": False,
    # PDF upload state
    "pdf_results": [],  # list of result dicts from pdf_to_db.process_pdf
}


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    state["logs"].append(f"[{ts}] {msg}")
    if len(state["logs"]) > 500:
        state["logs"] = state["logs"][-500:]


# ---- DB helpers ----
def get_conn():
    return pyodbc.connect(
        f"DRIVER={{{SQL_DRIVER}}};SERVER={SQL_SERVER};DATABASE={DATABASE};"
        f"Trusted_Connection=yes;TrustServerCertificate=yes;",
        timeout=15,
    )


def count_pending():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(f"""
            SELECT COUNT(*) FROM dbo.Invoices i
            INNER JOIN [{PORTAL_DB}].dbo.InvoiceInfo ii ON ii.InvoiceId = i.InvoiceId
            WHERE ii.Status = 'pending'
        """)
        return c.fetchone()[0]


def fetch_pending(limit=None):
    cols = (
        "i.InvoiceId, i.InvoiceNumber, i.SupplierTIN, i.BuyerName, i.BuyerTIN, "
        "i.Mykad, i.InvoiceDate, i.InvoiceTime, "
        "i.Subtotal, i.SSTAmount, i.TotalPayable, "
        "i.SupplierAddress, i.SupplierContact, "
        "i.BuyerAddress, i.BuyerContact"
    )
    join = (
        f"FROM dbo.Invoices i "
        f"INNER JOIN [{PORTAL_DB}].dbo.InvoiceInfo ii ON ii.InvoiceId = i.InvoiceId "
        f"WHERE ii.Status = 'pending' ORDER BY i.InvoiceId"
    )
    if limit:
        sql = f"SELECT TOP {int(limit)} {cols} {join}"
    else:
        sql = f"SELECT {cols} {join}"
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(sql)
        cols_out = [d[0] for d in c.description]
        return [dict(zip(cols_out, r)) for r in c.fetchall()]


def fetch_first_ids():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            "SELECT InvoiceNumber, MIN(InvoiceId) "
            "FROM dbo.Invoices GROUP BY InvoiceNumber"
        )
        return {n: i for n, i in c.fetchall()}


def fetch_invoice(iid):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(f"""
            SELECT i.InvoiceId, i.InvoiceNumber, i.SupplierName, i.SupplierTIN,
                   i.SupplierAddress, i.SupplierContact,
                   i.BuyerName, i.BuyerTIN, i.Mykad,
                   i.BuyerAddress, i.BuyerContact,
                   i.InvoiceDate, i.InvoiceTime,
                   i.Subtotal, i.SSTAmount, i.TotalPayable,
                   ii.Status, ii.UUID, ii.QRUrl, ii.VerifyUrl
            FROM dbo.Invoices i
            INNER JOIN [{PORTAL_DB}].dbo.InvoiceInfo ii ON ii.InvoiceId = i.InvoiceId
            WHERE i.InvoiceId = ?
        """, iid)
        cols = [d[0] for d in c.description]
        row = c.fetchone()
        return dict(zip(cols, row)) if row else None


def fetch_submitted():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(f"""
            SELECT ii.InvoiceId, i.InvoiceNumber, ii.UUID
            FROM [{PORTAL_DB}].dbo.InvoiceInfo ii
            INNER JOIN dbo.Invoices i ON i.InvoiceId = ii.InvoiceId
            WHERE ii.Status = 'submitted'
            ORDER BY ii.SubmittedAt DESC
        """)
        cols = [d[0] for d in c.description]
        return [dict(zip(cols, r)) for r in c.fetchall()]


def fetch_failed():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(f"""
            SELECT ii.InvoiceId, i.InvoiceNumber, ii.ErrorReason
            FROM [{PORTAL_DB}].dbo.InvoiceInfo ii
            INNER JOIN dbo.Invoices i ON i.InvoiceId = ii.InvoiceId
            WHERE ii.Status = 'failed'
            ORDER BY i.InvoiceId
        """)
        cols = [d[0] for d in c.description]
        return [dict(zip(cols, r)) for r in c.fetchall()]


def fetch_all_invoices():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(f"""
            SELECT i.InvoiceId, i.InvoiceNumber, i.SupplierName, i.SupplierTIN,
                   i.SupplierAddress, i.SupplierContact,
                   i.BuyerName, i.BuyerTIN, i.Mykad,
                   i.BuyerAddress, i.BuyerContact,
                   i.InvoiceDate, i.InvoiceTime,
                   i.Subtotal, i.SSTAmount, i.TotalPayable,
                   ii.Status
            FROM dbo.Invoices i
            INNER JOIN [{PORTAL_DB}].dbo.InvoiceInfo ii ON ii.InvoiceId = i.InvoiceId
            ORDER BY i.InvoiceId
        """)
        cols = [d[0] for d in c.description]
        return [dict(zip(cols, r)) for r in c.fetchall()]


def mark_invoice(iid, status, uuid_val=None, qr_url=None, verify_url=None, error=None):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(f"""
            UPDATE [{PORTAL_DB}].dbo.InvoiceInfo
            SET Status=?, UUID=?, QRUrl=?, VerifyUrl=?, ErrorReason=?, SubmittedAt=?
            WHERE InvoiceId=?
        """, status, uuid_val, qr_url, verify_url, error, datetime.now(), iid)
        conn.commit()


# ---- Formatting helpers ----
def fmt_date_val(v):
    if isinstance(v, datetime):
        return v.strftime("%Y-%m-%d")
    if isinstance(v, date):
        return v.strftime("%Y-%m-%d")
    return str(v)[:10]


def fmt_time_val(v):
    if isinstance(v, dtime):
        return v.strftime("%H:%M")
    if isinstance(v, timedelta):
        total_sec = int(v.total_seconds())
        hh = total_sec // 3600
        mm = (total_sec % 3600) // 60
        return f"{hh:02d}:{mm:02d}"
    if isinstance(v, datetime):
        return v.strftime("%H:%M")
    s = str(v)
    parts = s.split(":")
    if len(parts) >= 2:
        return f"{int(parts[0]):02d}:{int(parts[1]):02d}"
    return s[:5]


def fmt_amount(v):
    if v is None:
        return "0.00"
    return f"{float(v):.2f}"


def fmt_date_display(v):
    if isinstance(v, (datetime, date)):
        return v.strftime("%Y-%m-%d")
    return str(v)[:10]


def fmt_time_display(v):
    if isinstance(v, dtime):
        return v.strftime("%H:%M:%S")
    if isinstance(v, timedelta):
        total_sec = int(v.total_seconds())
        hh = total_sec // 3600
        mm = (total_sec % 3600) // 60
        ss = total_sec % 60
        return f"{hh:02d}:{mm:02d}:{ss:02d}"
    return str(v)


# ---- Playwright form automation ----
def find_form_frame(page):
    deadline = time.time() + 30
    while time.time() < deadline:
        for frame in page.frames:
            try:
                if frame.locator("#invNo").count() > 0 and frame.locator("#btn").count() > 0:
                    return frame
            except Exception:
                continue
        time.sleep(0.5)
    raise RuntimeError("Could not find form frame (timeout 30s)")


def process_invoice(page, inv):
    page.goto(FORM_URL, wait_until="domcontentloaded", timeout=60_000)
    frame = find_form_frame(page)
    fields = {
        "#invNo":       str(inv["InvoiceNumber"]),
        "#supplierTin": str(inv["SupplierTIN"]),
        "#buyerName":   str(inv["BuyerName"]),
        "#buyerTin":    str(inv["BuyerTIN"] or ""),
        "#buyerMykad":  str(inv.get("Mykad") or ""),
        "#invDate":     fmt_date_val(inv["InvoiceDate"]),
        "#invTime":     fmt_time_val(inv["InvoiceTime"]),
        "#total":       fmt_amount(inv["TotalPayable"]),
        "#sst":         fmt_amount(inv["SSTAmount"]),
    }
    for sel, val in fields.items():
        el = frame.locator(sel)
        el.wait_for(state="visible", timeout=10_000)
        el.fill("")
        el.fill(val)

    dialog_msg = {"value": None}
    def on_dialog(d):
        dialog_msg["value"] = d.message
        try:
            d.dismiss()
        except Exception:
            pass
    page.on("dialog", on_dialog)
    frame.locator("#btn").click()

    try:
        frame.locator("#result").wait_for(state="visible", timeout=30_000)
    except PWTimeout:
        if dialog_msg["value"]:
            return {"ok": False, "error": dialog_msg["value"]}
        return {"ok": False, "error": "timeout waiting for result"}

    return {
        "ok": True,
        "uuid": frame.locator("#uuid").inner_text().strip(),
        "verify_url": frame.locator("#vurl").inner_text().strip(),
        "qr_url": frame.locator("#qr").get_attribute("src") or "",
    }


# ---- Automation runner ----
def run_automation():
    state["running"] = True
    state["finished"] = False
    state["logs"] = []
    state["done"] = 0
    state["success"] = 0
    state["failed"] = 0
    log("Starting...")

    try:
        invoices = fetch_pending()
        state["total"] = len(invoices)
        log(f"Found {len(invoices)} pending invoices")

        if not invoices:
            log("Nothing to do - all invoices are already submitted!")
            state["finished"] = True
            state["running"] = False
            return

        first_id_by_number = fetch_first_ids()

        log("Validating invoices...")
        valid_invoices = []
        for inv in invoices:
            errs = check_invoices.validate(inv, first_id_by_number)
            if errs:
                state["failed"] += 1
                reason = "; ".join(errs)[:200]
                log(f"  VALIDATION FAIL: {inv['InvoiceNumber']} - {reason}")
                mark_invoice(inv["InvoiceId"], "failed", error=reason)
            else:
                valid_invoices.append(inv)
            state["done"] += 1

        log(f"Validation: {state['failed']} failed, {len(valid_invoices)} passed")

        if not valid_invoices:
            log("All invoices failed validation - nothing to submit.")
            log(f"DONE! success={state['success']} failed={state['failed']} total={state['total']}")
            state["finished"] = True
            state["running"] = False
            return

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            ctx = browser.new_context()
            page = ctx.new_page()

            for i, inv in enumerate(valid_invoices, 1):
                log(f"[{i}/{len(valid_invoices)}] {inv['InvoiceNumber']} (Id={inv['InvoiceId']})...")
                try:
                    result = process_invoice(page, inv)
                    if result["ok"]:
                        mark_invoice(
                            inv["InvoiceId"], "submitted",
                            uuid_val=result.get("uuid"),
                            qr_url=result.get("qr_url"),
                            verify_url=result.get("verify_url"),
                        )
                        state["success"] += 1
                        log(f"  OK  UUID={result['uuid'][:36]}")
                        log(f"  QR link: http://localhost:{PORT}/qr?id={inv['InvoiceId']}")
                    else:
                        mark_invoice(
                            inv["InvoiceId"], "failed",
                            error=result.get("error", "")[:200],
                        )
                        state["failed"] += 1
                        log(f"  FAILED: {result.get('error')}")
                except Exception as e:
                    state["failed"] += 1
                    log(f"  EXCEPTION: {e}")
                    try:
                        mark_invoice(inv["InvoiceId"], "failed", error=str(e)[:200])
                    except Exception:
                        pass
                    try:
                        page = ctx.new_page()
                    except Exception:
                        pass

                state["done"] += 1
                time.sleep(1)

            browser.close()

        log(f"DONE! success={state['success']} failed={state['failed']} total={state['total']}")
    except Exception as e:
        log(f"FATAL: {e}")
    finally:
        state["running"] = False
        state["finished"] = True


# ---- Multipart form-data parser (for PDF upload) ----
def parse_multipart(body, boundary):
    """Parse multipart/form-data body. Returns list of dicts with 'name', 'filename', 'data'."""
    boundary_bytes = ("--" + boundary).encode()
    parts = body.split(boundary_bytes)
    result = []

    for part in parts:
        # Skip empty parts and the closing boundary
        part = part.strip(b"\r\n")
        if not part or part == b"--" or part == b"--\r\n":
            continue

        # Split headers from content
        header_end = part.find(b"\r\n\r\n")
        if header_end == -1:
            continue

        header_block = part[:header_end].decode("utf-8", errors="replace")
        content = part[header_end + 4:]

        # Parse Content-Disposition
        name = None
        filename = None
        for line in header_block.split("\r\n"):
            if "Content-Disposition" in line:
                # Extract name="..."
                m = re.search(r'name="([^"]*)"', line)
                if m:
                    name = m.group(1)
                m = re.search(r'filename="([^"]*)"', line)
                if m:
                    filename = m.group(1)

        result.append({
            "name": name,
            "filename": filename,
            "data": content,
        })

    return result


# ---- QR Info Page ----
def render_qr_page(inv):
    qr_src = inv.get("QRUrl") or ""
    uuid_val = inv.get("UUID") or "N/A"
    inv_no = inv.get("InvoiceNumber") or "N/A"

    if qr_src:
        safe_src = html.escape(qr_src)
        qr_html = f'<img src="{safe_src}" alt="QR Code" style="max-width:250px;border-radius:10px;">'
    else:
        qr_html = '<div style="color:#f44336;font-size:16px;padding:40px;">No QR code available</div>'

    page = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>QR Info</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:'Segoe UI',sans-serif; background:#1a3d7c; color:#fff;
         min-height:100vh; display:flex; flex-direction:column; align-items:center; padding:40px; }
  .card { background:#0d2444; border-radius:16px; padding:40px; text-align:center;
          box-shadow:0 4px 20px rgba(0,0,0,0.3); max-width:500px; width:100%; }
  h1 { font-size:22px; margin-bottom:28px; color:#4fc3f7; }
  .field { margin-bottom:20px; }
  .field .lbl { font-size:12px; color:#8eafcc; margin-bottom:6px; text-transform:uppercase; letter-spacing:1px; }
  .field .val { font-size:18px; font-weight:bold; word-break:break-all; }
  .qr-img { margin:24px 0; }
  .back { margin-top:28px; }
  .back a { color:#4fc3f7; text-decoration:none; font-size:14px; }
  .back a:hover { text-decoration:underline; }
</style>
</head>
<body>
  <div class="card">
    <h1>Invoice QR Information</h1>
    <div class="field">
      <div class="lbl">Invoice Number</div>
      <div class="val">__INV_NO__</div>
    </div>
    <div class="qr-img">__QR_HTML__</div>
    <div class="field">
      <div class="lbl">UUID</div>
      <div class="val" style="font-family:'Consolas',monospace; font-size:14px;">__UUID__</div>
    </div>
    <div class="back">
      <a href="/submit">&#8592; Back to Submit Page</a>
    </div>
  </div>
</body>
</html>"""

    page = page.replace("__INV_NO__", html.escape(str(inv_no)))
    page = page.replace("__QR_HTML__", qr_html)
    page = page.replace("__UUID__", html.escape(str(uuid_val)))
    return page


# ---- Data Table Page (/) ----
DATA_TABLE_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>All Invoices</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:'Segoe UI',sans-serif; background:#1a3d7c; color:#fff; min-height:100vh;
         display:flex; flex-direction:column; align-items:center; padding:24px; }
  h1 { font-size:28px; margin-bottom:4px; }
  .sub { color:#8eafcc; font-size:14px; margin-bottom:24px; }
  .nav-link { position:absolute; top:24px; right:24px; color:#4fc3f7; text-decoration:none; font-size:14px; }
  .nav-link:hover { text-decoration:underline; }
  .btn-row { display:flex; gap:16px; margin-top:28px; }
  .btn-upload { font-size:18px; font-weight:bold; color:#fff; background:#1b7f3b; border:none;
                border-radius:12px; padding:14px 40px; cursor:pointer; transition:all .2s;
                text-decoration:none; display:inline-block; }
  .btn-upload:hover { background:#2a9d4f; transform:scale(1.03); }
  .btn-pdf { font-size:18px; font-weight:bold; color:#fff; background:#1565c0; border:none;
             border-radius:12px; padding:14px 40px; cursor:pointer; transition:all .2s;
             text-decoration:none; display:inline-block; }
  .btn-pdf:hover { background:#1976d2; transform:scale(1.03); }
  .table-wrap { width:95%; max-width:1200px; overflow-x:auto; border-radius:10px;
                box-shadow:0 4px 20px rgba(0,0,0,0.3); margin-top:16px; }
  table { border-collapse:collapse; width:100%; background:#0d2444; }
  th { background:#1a3d7c; color:#4fc3f7; font-size:12px; text-transform:uppercase;
       letter-spacing:0.5px; padding:12px 8px; text-align:left; position:sticky; top:0;
       border-bottom:2px solid #4fc3f7; white-space:nowrap; }
  td { padding:10px 8px; font-size:13px; border-bottom:1px solid #1a3d7c;
       white-space:nowrap; }
  tr:hover td { background:#102040; }
  .badge { padding:3px 10px; border-radius:12px; font-size:11px; font-weight:bold; text-transform:uppercase; }
  .badge-pending { background:#e65100; color:#fff; }
  .badge-submitted { background:#2e7d32; color:#fff; }
  .badge-failed { background:#c62828; color:#fff; }
  .summary { display:flex; gap:24px; margin:16px 0; }
  .stat { text-align:center; }
  .stat .val { font-size:28px; font-weight:bold; }
  .stat .lbl { font-size:12px; color:#8eafcc; }
  .btn-gen { font-size:11px; font-weight:bold; color:#fff; background:#6a1b9a; border:none;
             border-radius:6px; padding:6px 12px; cursor:pointer; transition:all .2s;
             text-decoration:none; display:inline-block; white-space:nowrap; }
  .btn-gen:hover { background:#8e24aa; }
</style>
</head>
<body>
  <a class="nav-link" href="/submit">Submit Page &rarr;</a>
  <h1>All Invoices</h1>
  <div class="sub">CompanyInvoiceDB.dbo.Invoices + MyInvoisPortal.dbo.InvoiceInfo</div>

  <div class="summary" id="summary">
    <div class="stat"><div class="val" id="cntPending" style="color:#e65100;">--</div><div class="lbl">Pending</div></div>
    <div class="stat"><div class="val" id="cntSubmitted" style="color:#4caf50;">--</div><div class="lbl">Submitted</div></div>
    <div class="stat"><div class="val" id="cntFailed" style="color:#f44336;">--</div><div class="lbl">Failed</div></div>
    <div class="stat"><div class="val" id="cntTotal" style="color:#4fc3f7;">--</div><div class="lbl">Total</div></div>
  </div>

  <div class="btn-row">
    <a class="btn-upload" href="/submit">Upload to MyInvois</a>
    <a class="btn-pdf" href="/upload">Upload PDF</a>
  </div>

  <div class="table-wrap">
    <table id="invTable">
      <thead>
        <tr>
          <th>ID</th><th>Invoice Number</th><th>Supplier Name</th><th>Supplier TIN</th>
          <th>Buyer Name</th><th>Buyer TIN</th><th>Mykad</th>
          <th>Date</th><th>Time</th><th>Subtotal</th><th>SST</th><th>Total</th><th>Status</th><th>Actions</th>
        </tr>
      </thead>
      <tbody id="invBody">
        <tr><td colspan="14" style="text-align:center;padding:40px;color:#8eafcc;">Loading...</td></tr>
      </tbody>
    </table>
  </div>

<script>
function loadTable() {
  fetch('/all-invoices').then(r=>r.json()).then(rows=>{
    var pending=0, submitted=0, failed=0;
    var body = document.getElementById('invBody');
    if (!rows || rows.length === 0) {
      body.innerHTML = '<tr><td colspan="14" style="text-align:center;padding:40px;color:#8eafcc;">No invoices found</td></tr>';
    } else {
      body.innerHTML = rows.map(function(r){
        var st = r.Status || 'pending';
        if (st === 'pending') pending++;
        else if (st === 'submitted') submitted++;
        else if (st === 'failed') failed++;
        var badge = '<span class="badge badge-'+st+'">'+st+'</span>';
        var actions = '';
        if (st === 'submitted') {
          actions = '<a class="btn-gen" href="/generate-invoice?id='+r.InvoiceId+'" target="_blank">Generate Invoice</a>';
        }
        return '<tr>'
          + '<td>'+r.InvoiceId+'</td>'
          + '<td style="font-weight:bold;">'+escapeHtml(r.InvoiceNumber)+'</td>'
          + '<td>'+escapeHtml(r.SupplierName||'')+'</td>'
          + '<td>'+escapeHtml(r.SupplierTIN||'')+'</td>'
          + '<td>'+escapeHtml(r.BuyerName||'')+'</td>'
          + '<td>'+escapeHtml(r.BuyerTIN||'')+'</td>'
          + '<td>'+escapeHtml(r.Mykad||'')+'</td>'
          + '<td>'+escapeHtml(r.InvoiceDate||'')+'</td>'
          + '<td>'+escapeHtml(r.InvoiceTime||'')+'</td>'
          + '<td>'+fmtMoney(r.Subtotal)+'</td>'
          + '<td>'+fmtMoney(r.SSTAmount)+'</td>'
          + '<td style="font-weight:bold;">'+fmtMoney(r.TotalPayable)+'</td>'
          + '<td>'+badge+'</td>'
          + '<td>'+actions+'</td>'
          + '</tr>';
      }).join('');
    }
    document.getElementById('cntPending').textContent = pending;
    document.getElementById('cntSubmitted').textContent = submitted;
    document.getElementById('cntFailed').textContent = failed;
    document.getElementById('cntTotal').textContent = rows.length;
  }).catch(function(e){
    document.getElementById('invBody').innerHTML = '<tr><td colspan="14" style="text-align:center;padding:40px;color:#f44336;">Error: '+escapeHtml(e.message)+'</td></tr>';
  });
}
function escapeHtml(s) { var d=document.createElement('div'); d.textContent=s; return d.innerHTML; }
function fmtMoney(v) { if(v==null) return '0.00'; return parseFloat(v).toFixed(2); }
loadTable();
setInterval(loadTable, 5000);
</script>
</body>
</html>"""


# ---- Submit Page (/submit) ----
SUBMIT_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Invoice Automation</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:'Segoe UI',sans-serif; background:#1a3d7c; color:#fff; min-height:100vh;
         display:flex; flex-direction:column; align-items:center; padding:24px; }
  h1 { font-size:28px; margin-bottom:4px; }
  .sub { color:#8eafcc; font-size:14px; margin-bottom:24px; }
  .nav-link { position:absolute; top:24px; right:24px; color:#4fc3f7; text-decoration:none; font-size:14px; }
  .nav-link:hover { text-decoration:underline; }
  .status { font-size:20px; margin-bottom:20px; }
  .status .num { font-size:36px; font-weight:bold; color:#4fc3f7; }
  .btn { font-size:22px; font-weight:bold; color:#fff; background:#1b7f3b; border:none;
         border-radius:12px; padding:18px 56px; cursor:pointer; transition:all .2s; }
  .btn:hover { background:#2a9d4f; transform:scale(1.03); }
  .btn:disabled { background:#555; cursor:not-allowed; transform:none; }
  .progress-bar { width:560px; height:24px; background:#0d2444; border-radius:12px;
                  overflow:hidden; margin:20px 0; }
  .progress-fill { height:100%; background:#4fc3f7; transition:width .3s; width:0%; }
  .progress-text { font-size:14px; color:#8eafcc; margin-bottom:12px; }
  .log { width:560px; height:240px; background:#0d2444; border-radius:10px; padding:12px;
         overflow-y:auto; font-family:'Consolas',monospace; font-size:12px;
         color:#a8d4a8; line-height:1.5; }
  .log div { white-space:pre-wrap; word-break:break-all; }
  .stats { display:flex; gap:24px; margin:12px 0; }
  .stat { text-align:center; }
  .stat .val { font-size:28px; font-weight:bold; }
  .stat .lbl { font-size:12px; color:#8eafcc; }
  .ok { color:#4caf50; } .fail { color:#f44336; }
  .qr-section { width:560px; margin-top:20px; }
  .qr-section h2 { font-size:18px; color:#4fc3f7; margin-bottom:12px; }
  .qr-list { background:#0d2444; border-radius:10px; padding:12px; max-height:200px; overflow-y:auto; }
  .qr-list a { color:#4fc3f7; text-decoration:none; font-size:14px; display:block; margin:6px 0; }
  .qr-list a:hover { text-decoration:underline; }
  .fail-section { width:560px; margin-top:20px; }
  .fail-section h2 { font-size:18px; color:#f44336; margin-bottom:12px; }
  .fail-list { background:#0d2444; border-radius:10px; padding:12px; max-height:300px; overflow-y:auto; }
  .fail-item { margin:8px 0; padding:8px 12px; background:#1a1520; border-radius:8px; border-left:3px solid #f44336; }
  .fail-item .num { font-weight:bold; color:#f44336; font-size:14px; }
  .fail-item .reason { font-size:12px; color:#ffab91; margin-top:4px; word-break:break-all; }
</style>
</head>
<body>
  <a class="nav-link" href="/">&larr; All Invoices</a>
  <h1>MyInvois Portal Auto-Submit</h1>
  <div class="sub">Fetch from SQL Server &rarr; Validate &rarr; Fill form &rarr; Submit &rarr; Write back</div>

  <div class="status">Pending invoices: <span class="num" id="pending">--</span></div>

  <button class="btn" id="startBtn" onclick="startAutomation()">SUBMIT INVOICES</button>

  <div class="stats" id="stats" style="display:none">
    <div class="stat"><div class="val" id="sTotal">0</div><div class="lbl">Total</div></div>
    <div class="stat"><div class="val ok" id="sOk">0</div><div class="lbl">Success</div></div>
    <div class="stat"><div class="val fail" id="sFail">0</div><div class="lbl">Failed</div></div>
  </div>

  <div class="progress-bar"><div class="progress-fill" id="pbar"></div></div>
  <div class="progress-text" id="ptext"></div>

  <div class="log" id="logbox"></div>

  <div class="qr-section" id="qrSection" style="display:none">
    <h2>QR Code Links</h2>
    <div class="qr-list" id="qrList"></div>
  </div>

  <div class="fail-section" id="failSection" style="display:none">
    <h2>Failed Invoices</h2>
    <div class="fail-list" id="failList"></div>
  </div>

<script>
function poll() {
  fetch('/status').then(r=>r.json()).then(d=>{
    document.getElementById('pending').textContent = d.pending;
    if (d.running) {
      document.getElementById('startBtn').disabled = true;
      document.getElementById('startBtn').textContent = 'RUNNING...';
      document.getElementById('stats').style.display = 'flex';
      document.getElementById('sTotal').textContent = d.total;
      document.getElementById('sOk').textContent = d.success;
      document.getElementById('sFail').textContent = d.failed;
      var pct = d.total > 0 ? (d.done / d.total * 100) : 0;
      document.getElementById('pbar').style.width = pct + '%';
      document.getElementById('ptext').textContent = d.done + ' / ' + d.total;
    } else if (d.finished) {
      document.getElementById('startBtn').disabled = false;
      document.getElementById('startBtn').textContent = 'SUBMIT INVOICES';
      document.getElementById('stats').style.display = 'flex';
      document.getElementById('sTotal').textContent = d.total;
      document.getElementById('sOk').textContent = d.success;
      document.getElementById('sFail').textContent = d.failed;
      var pct = d.total > 0 ? (d.done / d.total * 100) : 0;
      document.getElementById('pbar').style.width = pct + '%';
      document.getElementById('ptext').textContent = d.done + ' / ' + d.total;
    }
    var lb = document.getElementById('logbox');
    lb.innerHTML = d.logs.map(l=>'<div>'+l+'</div>').join('');
    lb.scrollTop = lb.scrollHeight;
  });
}
setInterval(poll, 1000);
poll();

function loadQrLinks() {
  fetch('/submitted').then(r=>r.json()).then(subs=>{
    var sec = document.getElementById('qrSection');
    var list = document.getElementById('qrList');
    if (subs && subs.length > 0) {
      sec.style.display = 'block';
      list.innerHTML = subs.map(function(s){
        var uuid = s.UUID ? (s.UUID.length > 36 ? s.UUID.substring(0,36)+'...' : s.UUID) : 'N/A';
        return '<a href="/qr?id='+s.InvoiceId+'" target="_blank">'+s.InvoiceNumber+' &rarr; '+uuid+'</a>';
      }).join('');
    } else {
      sec.style.display = 'none';
    }
  }).catch(function(){});
}
loadQrLinks();
setInterval(loadQrLinks, 5000);

function loadFailed() {
  fetch('/failed').then(r=>r.json()).then(fails=>{
    var sec = document.getElementById('failSection');
    var list = document.getElementById('failList');
    if (fails && fails.length > 0) {
      sec.style.display = 'block';
      list.innerHTML = fails.map(function(f){
        var reason = f.ErrorReason || 'Unknown error';
        return '<div class="fail-item">'
          + '<div class="num">'+escapeHtml(f.InvoiceNumber)+' (ID: '+f.InvoiceId+')</div>'
          + '<div class="reason">'+escapeHtml(reason)+'</div>'
          + '</div>';
      }).join('');
    } else {
      sec.style.display = 'none';
    }
  }).catch(function(){});
}
loadFailed();
setInterval(loadFailed, 5000);

function escapeHtml(s) { var d=document.createElement('div'); d.textContent=s; return d.innerHTML; }

function startAutomation() {
  fetch('/start', {method:'POST'}).then(r=>r.json()).then(d=>{
    if (d.error) { alert(d.error); }
  });
}
</script>
</body>
</html>"""


# ---- PDF Upload Page (/upload) ----
UPLOAD_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Upload PDF Invoice</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:'Segoe UI',sans-serif; background:#1a3d7c; color:#fff; min-height:100vh;
         display:flex; flex-direction:column; align-items:center; padding:24px; }
  h1 { font-size:28px; margin-bottom:4px; }
  .sub { color:#8eafcc; font-size:14px; margin-bottom:24px; }
  .nav-link { position:absolute; top:24px; right:24px; color:#4fc3f7; text-decoration:none; font-size:14px; }
  .nav-link:hover { text-decoration:underline; }
  .upload-card { background:#0d2444; border-radius:16px; padding:40px; text-align:center;
                 box-shadow:0 4px 20px rgba(0,0,0,0.3); max-width:600px; width:100%; }
  .drop-zone { border:2px dashed #4fc3f7; border-radius:12px; padding:48px 24px;
               margin:20px 0; cursor:pointer; transition:all .3s; }
  .drop-zone:hover, .drop-zone.dragover { background:#102040; border-color:#4fc3f7; }
  .drop-zone p { color:#8eafcc; font-size:16px; margin:8px 0; }
  .drop-zone .icon { font-size:48px; margin-bottom:12px; }
  #fileInput { display:none; }
  .file-name { color:#4fc3f7; font-size:14px; margin:8px 0; }
  .btn { font-size:20px; font-weight:bold; color:#fff; background:#1565c0; border:none;
         border-radius:12px; padding:14px 48px; cursor:pointer; transition:all .2s;
         margin:12px 0; }
  .btn:hover { background:#1976d2; transform:scale(1.03); }
  .btn:disabled { background:#555; cursor:not-allowed; transform:none; }
  .progress { margin:16px 0; }
  .progress-bar { width:100%; height:8px; background:#102040; border-radius:4px; overflow:hidden; }
  .progress-fill { height:100%; background:#4fc3f7; width:0%; transition:width .3s; }
  .result-card { background:#0d2444; border-radius:10px; padding:20px; margin:16px 0;
                 text-align:left; max-width:600px; width:100%; }
  .result-card.success { border-left:4px solid #4caf50; }
  .result-card.error { border-left:4px solid #f44336; }
  .result-card h3 { font-size:16px; margin-bottom:12px; }
  .result-card .field { margin:4px 0; font-size:13px; }
  .result-card .field .lbl { color:#8eafcc; display:inline-block; width:140px; }
  .result-card .field .val { color:#fff; font-weight:bold; }
  .result-card .method { font-size:11px; color:#8eafcc; margin-top:8px; }
  .result-card .warning { color:#ffab91; font-size:12px; margin-top:8px; }
  .summary { background:#0d2444; border-radius:10px; padding:16px 20px; margin:16px 0;
             text-align:center; max-width:600px; width:100%; font-size:15px; color:#8eafcc; }
  .summary b { color:#4caf50; }
</style>
</head>
<body>
  <a class="nav-link" href="/">&larr; All Invoices</a>
  <h1>Upload PDF Invoice</h1>
  <div class="sub">Read PDF &rarr; Extract data per page &rarr; Insert into Invoices + InvoiceInfo (pending)</div>
  <div class="sub" style="font-size:12px;">Supports multi-page PDF: each page = one invoice</div>

  <div class="upload-card">
    <div class="drop-zone" id="dropZone" onclick="document.getElementById('fileInput').click()">
      <div class="icon">&#128196;</div>
      <p><b>Click to select</b> or drag &amp; drop a PDF here</p>
      <p style="font-size:12px;color:#8eafcc;">PDF files only (*.pdf)</p>
    </div>
    <input type="file" id="fileInput" accept=".pdf" />
    <div class="file-name" id="fileName"></div>
    <button class="btn" id="uploadBtn" onclick="uploadPDF()" disabled>Process PDF</button>
    <div class="progress" id="progress" style="display:none">
      <div class="progress-bar"><div class="progress-fill" id="progFill"></div></div>
    </div>
  </div>

  <div id="results"></div>

<script>
var selectedFile = null;

document.getElementById('fileInput').addEventListener('change', function(e) {
  if (e.target.files.length > 0) {
    var f = e.target.files[0];
    if (f.name.toLowerCase().endsWith('.pdf')) {
      selectedFile = f;
      document.getElementById('fileName').textContent = 'Selected: ' + f.name + ' (' + (f.size/1024).toFixed(1) + ' KB)';
      document.getElementById('uploadBtn').disabled = false;
    } else {
      alert('Please select a PDF file.');
      selectedFile = null;
      document.getElementById('uploadBtn').disabled = true;
    }
  }
});

// Drag & drop
var dropZone = document.getElementById('dropZone');
dropZone.addEventListener('dragover', function(e) { e.preventDefault(); dropZone.classList.add('dragover'); });
dropZone.addEventListener('dragleave', function(e) { dropZone.classList.remove('dragover'); });
dropZone.addEventListener('drop', function(e) {
  e.preventDefault();
  dropZone.classList.remove('dragover');
  if (e.dataTransfer.files.length > 0) {
    var f = e.dataTransfer.files[0];
    if (f.name.toLowerCase().endsWith('.pdf')) {
      selectedFile = f;
      document.getElementById('fileInput').files = e.dataTransfer.files;
      document.getElementById('fileName').textContent = 'Selected: ' + f.name + ' (' + (f.size/1024).toFixed(1) + ' KB)';
      document.getElementById('uploadBtn').disabled = false;
    } else {
      alert('Please drop a PDF file.');
    }
  }
});

function uploadPDF() {
  if (!selectedFile) return;
  document.getElementById('uploadBtn').disabled = true;
  document.getElementById('uploadBtn').textContent = 'Processing...';
  document.getElementById('progress').style.display = 'block';
  document.getElementById('progFill').style.width = '30%';

  var formData = new FormData();
  formData.append('pdf', selectedFile);

  fetch('/pdf-process', { method:'POST', body: formData })
    .then(r => r.json())
    .then(d => {
      document.getElementById('progFill').style.width = '100%';
      var results = document.getElementById('results');
      var html = '';

      // d.results is an array of per-page results
      var items = d.results || [];
      if (items.length === 0) {
        html = '<div class="result-card error"><h3>&#10007; No results returned</h3></div>';
      } else {
        // Summary banner
        html += '<div class="summary">'
          + '<b>' + d.success + '</b> success'
          + (d.failed > 0 ? ', <b style="color:#f44336">' + d.failed + '</b> failed' : '')
          + ' &mdash; ' + d.total + ' page(s) processed'
          + '</div>';

        for (var i = 0; i < items.length; i++) {
          var r = items[i];
          if (r.ok) {
            var data = r.data || {};
            html += '<div class="result-card success">'
              + '<h3>&#10003; Page ' + r.page + ' &mdash; InvoiceId = ' + r.invoice_id + '</h3>'
              + '<div class="field"><span class="lbl">Invoice Number:</span><span class="val">' + esc(data.invoice_number) + '</span></div>'
              + '<div class="field"><span class="lbl">Supplier:</span><span class="val">' + esc(data.supplier_name) + '</span></div>'
              + '<div class="field"><span class="lbl">Supplier TIN:</span><span class="val">' + esc(data.supplier_tin) + '</span></div>'
              + '<div class="field"><span class="lbl">Buyer:</span><span class="val">' + esc(data.buyer_name) + '</span></div>'
              + '<div class="field"><span class="lbl">Buyer TIN:</span><span class="val">' + esc(data.buyer_tin) + '</span></div>'
              + '<div class="field"><span class="lbl">MyKad:</span><span class="val">' + esc(data.buyer_mykad) + '</span></div>'
              + '<div class="field"><span class="lbl">Date/Time:</span><span class="val">' + esc(data.invoice_date_time) + '</span></div>'
              + '<div class="field"><span class="lbl">Subtotal:</span><span class="val">' + fmtM(data.subtotal) + '</span></div>'
              + '<div class="field"><span class="lbl">SST:</span><span class="val">' + fmtM(data.sst_amount) + '</span></div>'
              + '<div class="field"><span class="lbl">Total:</span><span class="val">' + fmtM(data.total_payable) + '</span></div>'
              + '<div class="method">Method: ' + r.method + ' | Status: pending</div>';
            if (r.warning) html += '<div class="warning">&#9888; ' + esc(r.warning) + '</div>';
            html += '<div style="margin-top:12px;"><a href="/" style="color:#4fc3f7;text-decoration:none;">&rarr; View in data table</a></div>';
            html += '</div>';
          } else {
            html += '<div class="result-card error">'
              + '<h3>&#10007; Page ' + (r.page || '?') + ' &mdash; Failed</h3>'
              + '<div class="field"><span class="val">' + esc(r.error) + '</span></div>'
              + '</div>';
          }
        }
      }
      results.innerHTML = html;
      document.getElementById('uploadBtn').disabled = false;
      document.getElementById('uploadBtn').textContent = 'Process PDF';
      document.getElementById('progress').style.display = 'none';
      document.getElementById('progFill').style.width = '0%';
    })
    .catch(e => {
      document.getElementById('results').innerHTML = '<div class="result-card error"><h3>&#10007; Error</h3><div class="field"><span class="val">' + esc(e.message) + '</span></div></div>';
      document.getElementById('uploadBtn').disabled = false;
      document.getElementById('uploadBtn').textContent = 'Process PDF';
      document.getElementById('progress').style.display = 'none';
    });
}

function esc(s) { if (s == null) return ''; var d=document.createElement('div'); d.textContent=s; return d.innerHTML; }
function fmtM(v) { if (v == null) return 'N/A'; return parseFloat(v).toFixed(2); }
</script>
</body>
</html>"""


# ---- HTTP Server ----
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path == "/":
            self._send(200, "text/html", DATA_TABLE_PAGE)
        elif path == "/submit":
            self._send(200, "text/html", SUBMIT_PAGE)
        elif path == "/upload":
            self._send(200, "text/html", UPLOAD_PAGE)
        elif path == "/status":
            try:
                pending = count_pending()
            except Exception:
                pending = -1
            data = {
                "running": state["running"],
                "finished": state["finished"],
                "total": state["total"],
                "done": state["done"],
                "success": state["success"],
                "failed": state["failed"],
                "pending": pending,
                "logs": state["logs"][-100:],
            }
            self._send(200, "application/json", json.dumps(data))
        elif path == "/all-invoices":
            try:
                rows = fetch_all_invoices()
                for r in rows:
                    r["InvoiceDate"] = fmt_date_display(r.get("InvoiceDate"))
                    r["InvoiceTime"] = fmt_time_display(r.get("InvoiceTime"))
                    if r.get("Subtotal") is not None:
                        r["Subtotal"] = float(r["Subtotal"])
                    if r.get("SSTAmount") is not None:
                        r["SSTAmount"] = float(r["SSTAmount"])
                    if r.get("TotalPayable") is not None:
                        r["TotalPayable"] = float(r["TotalPayable"])
                self._send(200, "application/json", json.dumps(rows))
            except Exception as e:
                self._send(500, "application/json",
                           json.dumps({"error": str(e)}))
        elif path == "/submitted":
            try:
                subs = fetch_submitted()
                self._send(200, "application/json", json.dumps(subs))
            except Exception as e:
                self._send(500, "application/json",
                           json.dumps({"error": str(e)}))
        elif path == "/failed":
            try:
                fails = fetch_failed()
                self._send(200, "application/json", json.dumps(fails))
            except Exception as e:
                self._send(500, "application/json",
                           json.dumps({"error": str(e)}))
        elif path == "/qr":
            iid_str = params.get("id", [None])[0]
            if not iid_str:
                self._send(400, "text/plain", "Missing id parameter")
                return
            try:
                iid = int(iid_str)
            except ValueError:
                self._send(400, "text/plain", "Invalid id")
                return
            inv = fetch_invoice(iid)
            if not inv:
                self._send(404, "text/plain", "Invoice not found")
                return
            self._send(200, "text/html", render_qr_page(inv))
        elif path == "/generate-invoice":
            iid_str = params.get("id", [None])[0]
            if not iid_str:
                self._send(400, "text/plain", "Missing id parameter")
                return
            try:
                iid = int(iid_str)
            except ValueError:
                self._send(400, "text/plain", "Invalid id")
                return
            try:
                inv = invoice_excel_generator.fetch_invoice_full(iid)
                if not inv:
                    self._send(404, "text/plain", "Invoice not found")
                    return
                xlsx_bytes = invoice_excel_generator.generate_invoice_excel(iid)
                filename = f"Invoice_{iid}_{inv.get('InvoiceNumber','unknown')}.xlsx"
                self.send_response(200)
                self.send_header("Content-Type",
                                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                self.send_header("Content-Disposition",
                                 f'attachment; filename="{filename}"')
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(xlsx_bytes)))
                self.end_headers()
                self.wfile.write(xlsx_bytes)
            except Exception as e:
                self._send(500, "text/plain", f"Excel generation failed: {e}")
        else:
            self._send(404, "text/plain", "Not found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/start":
            if state["running"]:
                self._send(200, "application/json",
                           json.dumps({"error": "Already running"}))
                return
            t = threading.Thread(target=run_automation, daemon=True)
            t.start()
            self._send(200, "application/json", json.dumps({"ok": True}))

        elif path == "/pdf-process":
            self._handle_pdf_upload()

        else:
            self._send(404, "text/plain", "Not found")

    def _handle_pdf_upload(self):
        """Handle multipart/form-data file upload for PDF processing."""
        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            self._send(400, "application/json",
                       json.dumps({"ok": False, "error": "Expected multipart/form-data"}))
            return

        # Extract boundary
        boundary = None
        for part in content_type.split(";"):
            part = part.strip()
            if part.startswith("boundary="):
                boundary = part[len("boundary="):]
                # Remove surrounding quotes if present
                if boundary.startswith('"') and boundary.endswith('"'):
                    boundary = boundary[1:-1]
                break

        if not boundary:
            self._send(400, "application/json",
                       json.dumps({"ok": False, "error": "No boundary in Content-Type"}))
            return

        # Read body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        # Parse multipart
        try:
            parts = parse_multipart(body, boundary)
        except Exception as e:
            self._send(500, "application/json",
                       json.dumps({"ok": False, "error": f"Parse error: {e}"}))
            return

        # Find the PDF file part
        pdf_part = None
        for p in parts:
            if p.get("filename") and p.get("name") == "pdf":
                pdf_part = p
                break

        if not pdf_part:
            self._send(400, "application/json",
                       json.dumps({"ok": False, "error": "No PDF file in upload"}))
            return

        filename = pdf_part["filename"]
        pdf_data = pdf_part["data"]

        if not filename.lower().endswith(".pdf"):
            self._send(400, "application/json",
                       json.dumps({"ok": False, "error": "File must be a PDF"}))
            return

        # Save to temp file
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                suffix=".pdf", delete=False, dir=tempfile.gettempdir()
            ) as tmp:
                tmp.write(pdf_data)
                tmp_path = tmp.name

            # Process the PDF (supports multi-page: each page = one invoice)
            results = pdf_to_db.process_pdf_pages(tmp_path)
            success = sum(1 for r in results if r.get("ok"))
            response = {
                "results": results,
                "total": len(results),
                "success": success,
                "failed": len(results) - success,
            }
            self._send(200, "application/json",
                       json.dumps(response, default=str))

        except Exception as e:
            self._send(500, "application/json",
                       json.dumps({"ok": False, "error": str(e)}))
        finally:
            # Clean up temp file
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

    def _send(self, code, ctype, body):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, *args):
        pass


def open_browser():
    import webbrowser
    time.sleep(1.5)
    webbrowser.open(f"http://localhost:{PORT}")


def main():
    print(f"Invoice Automation server: http://localhost:{PORT}")
    print("  /         -> All Invoices data table")
    print("  /submit   -> Submit page (SUBMIT button)")
    print("  /upload   -> PDF upload page (read PDF -> insert into DB)")
    print("  /qr?id=N  -> QR info page")
    print("  /generate-invoice?id=N  -> Download invoice Excel (submitted rows, with QR code)")
    print("Opening browser...")
    threading.Thread(target=open_browser, daemon=True).start()
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
