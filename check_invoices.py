"""
Invoice validation layer — checks each pending invoice against business rules
before it is sent to the MyInvois portal. Bad invoices are marked 'failed' with
a reason; good ones stay 'pending' for the agent to submit.

Updated for the split-database schema and new fields:
  CompanyInvoiceDB.dbo.Invoices       — invoice data (InvoiceId ... TotalPayable,
                                        SupplierAddress, SupplierContact,
                                        BuyerAddress, BuyerContact)
  MyInvoisPortal.dbo.InvoiceInfo      — submission status (Status, UUID, QRUrl, ...)
"""
import re
import sys
from decimal import Decimal, ROUND_HALF_UP

# ---- CONFIG -----------------------------------------------------------------
SERVER = "localhost"
DATABASE = "CompanyInvoiceDB"
PORTAL_DB = "MyInvoisPortal"
DRIVER = "ODBC Driver 17 for SQL Server"
# ----------------------------------------------------------------------------

SST_RATE = Decimal("0.08")
TOLERANCE = Decimal("0.01")
CENT = Decimal("0.01")

# ---- Format patterns --------------------------------------------------------
COMPANY_TIN = re.compile(r"^C\d{10}$")               # C + 10 digits
MYKAD_12 = re.compile(r"^\d{12}$")                   # 12 digits, no dashes (input)
MYKAD_DASH3 = re.compile(r"^\d{6}-\d{2}-\d{3}$")     # YYMMDD-PP-PPP  (11 digits, input)
MYKAD_DASH4 = re.compile(r"^\d{6}-\d{2}-\d{4}$")    # YYMMDD-PP-PPPP (12 digits, REQUIRED)

EMAIL_RE = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)
PHONE_RE = re.compile(r"^[+]?[\d\s\-()]{7,}$")


def money(x):
    return Decimal(str(x)).quantize(CENT, rounding=ROUND_HALF_UP)


def is_valid_contact(value):
    """Return True if *value* looks like an email address or a phone number.

    Handles combined formats like ``07-2345678 | sales@example.com``
    where phone and email are separated by a pipe ``|``.
    """
    v = value.strip()

    # Combined format: phone | email  (or email | phone)
    if "|" in v:
        parts = [p.strip() for p in v.split("|") if p.strip()]
        # At least one part must be a valid email or phone
        return any(_is_single_contact(p) for p in parts)

    return _is_single_contact(v)


def _is_single_contact(v):
    """Check a single email or phone token."""
    if "@" in v:
        return bool(EMAIL_RE.match(v))
    digits = re.sub(r"[^\d]", "", v)
    return len(digits) >= 7 and bool(PHONE_RE.match(v))


def is_valid_mykad(value):
    """Return True if *value* is a valid MyKad in the REQUIRED format:
    xxxxxx-xx-xxxx (YYMMDD-PP-PPPP, 12 digits with dashes)."""
    v = value.strip()
    return bool(MYKAD_DASH4.match(v))


def normalize_mykad(value):
    """Convert any MyKad input to the REQUIRED format xxxxxx-xx-xxxx.
    Handles:
      - 12 digits no dashes  -> 6-2-4
      - 6-2-3 (11 digits)    -> pad to 6-2-4
      - already 6-2-4        -> unchanged
    """
    v = (value or "").strip()
    if MYKAD_DASH4.match(v):
        return v
    if MYKAD_12.match(v):
        return f"{v[:6]}-{v[6:8]}-{v[8:12]}"
    if MYKAD_DASH3.match(v):
        parts = v.split("-")
        return f"{parts[0]}-{parts[1]}-{parts[2].zfill(4)}"
    return v


def validate(row, first_id_by_number):
    """Return a list of problems for one invoice (empty list = OK).

    row: dict with InvoiceId, InvoiceNumber, SupplierTIN, SupplierName,
         SupplierAddress, SupplierContact,
         BuyerName, BuyerTIN, Mykad, BuyerAddress, BuyerContact,
         InvoiceDate, InvoiceTime, Subtotal, SSTAmount, TotalPayable
    """
    errors = []

    sub = money(row["Subtotal"])
    sst = money(row["SSTAmount"])
    total = money(row["TotalPayable"])

    # ---- Supplier TIN — must be C + 10 digits -------------------------------
    supplier_tin = (row["SupplierTIN"] or "").strip()
    if not supplier_tin:
        errors.append("Supplier TIN is missing")
    elif not COMPANY_TIN.match(supplier_tin):
        errors.append(f"Supplier TIN invalid ({supplier_tin!r}); expected C+10 digits")

    # ---- Supplier Address — required, minimum length ------------------------
    supplier_addr = (row.get("SupplierAddress") or "").strip()
    if not supplier_addr:
        errors.append("Supplier address is missing")
    elif len(supplier_addr) < 10:
        errors.append(
            f"Supplier address too short ({supplier_addr!r}); "
            f"expected a full street address"
        )

    # ---- Supplier Contact — required, must be email or phone ---------------
    supplier_contact = (row.get("SupplierContact") or "").strip()
    if not supplier_contact:
        errors.append("Supplier contact is missing")
    elif not is_valid_contact(supplier_contact):
        errors.append(
            f"Supplier contact invalid ({supplier_contact!r}); "
            f"expected email or phone number"
        )

    # ---- Buyer TIN — required, must be C + 10 digits -----------------------
    buyer_tin = (row["BuyerTIN"] or "").strip()
    if not buyer_tin:
        errors.append("Buyer TIN is missing")
    elif not COMPANY_TIN.match(buyer_tin):
        errors.append(f"Buyer TIN invalid ({buyer_tin!r}); expected C+10 digits")

    # ---- MyKad — must be xxxxxx-xx-xxxx (YYMMDD-PP-PPPP) ------------------
    mykad = (row.get("Mykad") or "").strip()
    if mykad and not is_valid_mykad(mykad):
        errors.append(
            f"MyKad invalid ({mykad!r}); "
            f"expected format xxxxxx-xx-xxxx"
        )

    # ---- Buyer name ---------------------------------------------------------
    if not (row["BuyerName"] or "").strip():
        errors.append("Buyer name missing")

    # ---- Buyer Address — required, minimum length --------------------------
    buyer_addr = (row.get("BuyerAddress") or "").strip()
    if not buyer_addr:
        errors.append("Buyer address is missing")
    elif len(buyer_addr) < 10:
        errors.append(
            f"Buyer address too short ({buyer_addr!r}); "
            f"expected a full street address"
        )

    # ---- Buyer Contact — required, must be email or phone -------------------
    buyer_contact = (row.get("BuyerContact") or "").strip()
    if not buyer_contact:
        errors.append("Buyer contact is missing")
    elif not is_valid_contact(buyer_contact):
        errors.append(
            f"Buyer contact invalid ({buyer_contact!r}); "
            f"expected email or phone number"
        )

    # ---- Amount checks ------------------------------------------------------
    if total <= 0 or sub <= 0:
        errors.append("Total or subtotal is zero/negative")
    else:
        expected_sst = (sub * SST_RATE).quantize(CENT, rounding=ROUND_HALF_UP)
        if abs(sst - expected_sst) > TOLERANCE:
            errors.append(f"SST is {sst} but 8% of subtotal {sub} is {expected_sst}")
        if abs(total - (sub + sst)) > TOLERANCE:
            errors.append(f"Total {total} != subtotal {sub} + SST {sst} = {sub + sst}")

    # ---- Duplicate invoice number ------------------------------------------
    first_id = first_id_by_number.get(row["InvoiceNumber"])
    if first_id is not None and row["InvoiceId"] != first_id:
        errors.append(
            f"Duplicate invoice number {row['InvoiceNumber']} "
            f"(first used by InvoiceId {first_id})")

    return errors


# ---- database helpers --------------------------------------------------------

def connect():
    import pyodbc
    conn_str = (
        f"DRIVER={{{DRIVER}}};SERVER={SERVER};DATABASE={DATABASE};"
        f"Trusted_Connection=yes;TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str, timeout=15)


def fetch_pending(cur):
    """Fetch pending invoices — JOIN Invoices with InvoiceInfo (cross-DB)."""
    cur.execute(f"""
        SELECT i.InvoiceId, i.InvoiceNumber, i.SupplierTIN, i.BuyerName, i.BuyerTIN,
               i.Mykad, i.InvoiceDate, i.InvoiceTime,
               i.Subtotal, i.SSTAmount, i.TotalPayable,
               i.SupplierAddress, i.SupplierContact,
               i.BuyerAddress, i.BuyerContact
        FROM dbo.Invoices i
        INNER JOIN [{PORTAL_DB}].dbo.InvoiceInfo ii ON ii.InvoiceId = i.InvoiceId
        WHERE ii.Status = 'pending'
        ORDER BY i.InvoiceId
    """)
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def first_ids(cur):
    cur.execute(
        "SELECT InvoiceNumber, MIN(InvoiceId) FROM dbo.Invoices GROUP BY InvoiceNumber")
    return {n: i for n, i in cur.fetchall()}


def run(dry_run=False):
    """Check all pending invoices, mark bad ones as 'failed'."""
    conn = connect()
    cur = conn.cursor()
    rows = fetch_pending(cur)
    first = first_ids(cur)

    failed = []
    for r in rows:
        errs = validate(r, first)
        if errs:
            failed.append((r, errs))
            if not dry_run:
                cur.execute(f"""
                    UPDATE [{PORTAL_DB}].dbo.InvoiceInfo
                    SET Status='failed', ErrorReason=?
                    WHERE InvoiceId=?
                """, "; ".join(errs)[:200], r["InvoiceId"])
    if not dry_run:
        conn.commit()
    conn.close()

    print(f"Checked {len(rows)} pending invoices"
          + ("  [DRY RUN]" if dry_run else ""))
    print(f"  passed: {len(rows) - len(failed)}")
    print(f"  failed: {len(failed)}")
    for r, errs in failed:
        print(f"\n  InvoiceId {r['InvoiceId']:>3}  {r['InvoiceNumber']}")
        for e in errs:
            print(f"      - {e}")


if __name__ == "__main__":
    args = set(sys.argv[1:])
    run(dry_run="--dry-run" in args)
