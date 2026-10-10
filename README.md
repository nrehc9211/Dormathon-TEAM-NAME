# SmartInvoice AI — Automated Invoice Processing System

An end-to-end invoice automation system that extracts data from PDF invoices, validates it, submits it to a simulated MyInvois Portal (via Google Apps Script), and generates branded Excel invoices with embedded QR codes for verification.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Prerequisites & Environment](#prerequisites--environment)
4. [Python Package Installation](#python-package-installation)
5. [Database Setup](#database-setup)
6. [AI Model Setup (Ollama)](#ai-model-setup-ollama)
7. [Playwright Browser Setup](#playwright-browser-setup)
8. [Excel Template Setup](#excel-template-setup)
9. [Google Apps Script (MyInvois Portal Simulator)](#google-apps-script-myinvois-portal-simulator)
10. [File Structure](#file-structure)
11. [Configuration Reference](#configuration-reference)
12. [How to Run](#how-to-run)
13. [Web GUI Endpoints](#web-gui-endpoints)
14. [Data Formats & Validation Rules](#data-formats--validation-rules)
15. [PDF Extraction Pipeline](#pdf-extraction-pipeline)
16. [Excel Cell Mapping](#excel-cell-mapping)
17. [Auto-Restart Watchdog](#auto-restart-watchdog)
18. [Troubleshooting](#troubleshooting)

---

## System Overview

This system automates the complete invoice lifecycle:

```
PDF Invoice → Extract Data → Insert to DB → Validate → Submit to MyInvois Portal → Write back UUID/QR → Generate Excel Invoice
```

**Key capabilities:**

| Feature | Description |
|---------|-------------|
| PDF Upload & Extraction | Upload PDF invoices via web GUI; extract structured data using AI (Ollama) or regex fallback |
| Database Storage | Store all invoice data in SQL Server with two linked databases |
| Data Validation | Strict format enforcement for TIN, MyKad, contacts, amounts, and SST calculation |
| Portal Submission | Automated browser form submission to a Google Apps Script endpoint (simulated MyInvois Portal) |
| QR Code & UUID Write-back | Submission results (UUID, QR URL, Verify URL) are stored and embedded in generated Excel invoices |
| Excel Invoice Generation | Fill a branded Excel template with invoice data + embedded QR code |
| Web Dashboard | Real-time table view of all invoices, submission status, logs, and QR viewer |
| Auto-Restart | Batch watchdog keeps the server running if it crashes |

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Web GUI (Port 8765)                         │
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ Data     │  │ Submit   │  │ Upload   │  │ QR Viewer         │  │
│  │ Table    │  │ Page     │  │ Page     │  │ /qr?id=N          │  │
│  │ /        │  │ /submit  │  │ /upload  │  │                   │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───────────────────┘  │
│       │              │              │                               │
└───────┼──────────────┼──────────────┼───────────────────────────────┘
        │              │              │
        ▼              ▼              ▼
┌──────────────┐ ┌───────────┐ ┌──────────────┐
│  SQL Server  │ │ Playwright│ │  pdf_to_db   │
│              │ │  Browser  │ │  (Ollama AI  │
│ ┌──────────┐ │ │  (Chromium│ │   + Regex)   │
│ │CompanyIn-│ │ │   headless│ │              │
│ │voiceDB   │ │ │   )       │ │  extract_    │
│ │ dbo.Invo-│ │ │           │ │  pdf_text()  │
│ │ ices     │ │ │  Fill form│ │  (pypdf)     │
│ └──────────┘ │ │  fields   │ │              │
│ ┌──────────┐ │ │  Click    │ │  parse_invoice│
│ │MyInvois- │ │ │  submit   │ │  _from_text()│
│ │Portal    │ │ │  Get UUID │ │              │
│ │ dbo.Invo-│ │ │  + QR URL │ │  INSERT to   │
│ │  iceInfo │ │ └─────┬─────┘ │  both DBs    │
│ └──────────┘ │       │       └──────┬───────┘
└──────────────┘       │              │
                       ▼              │
              ┌────────────────┐      │
              │ Google Apps    │      │
              │ Script Web App │      │
              │ (MyInvois      │      │
              │  Portal Form)  │      │
              │                │      │
              │ Returns:       │      │
              │  - UUID        │      │
              │  - QR URL      │      │
              │  - Verify URL  │      │
              └────────────────┘      │
                                      │
                    ┌─────────────────┘
                    ▼
           ┌──────────────────┐
           │ invoice_excel_   │
           │ generator.py     │
           │                  │
           │ Load template    │
           │ Fill cells       │
           │ Embed QR image   │
           │ Return .xlsx     │
           └──────────────────┘
```

---

## Prerequisites & Environment

### 1. Operating System

- **Windows 10/11** (tested on Windows 11)
- The `START_INVOICE_AUTO.bat` watchdog is Windows-only
- Linux/macOS: run `python invoice_web_gui.py` directly

### 2. Python

- **Python 3.10+** (tested on Python 3.13)
- Download: https://www.python.org/downloads/
- During installation, check **"Add Python to PATH"**

### 3. SQL Server

- **SQL Server 2019+** (Express edition is sufficient)
- Download SQL Server Express: https://www.microsoft.com/en-us/sql-server/sql-server-downloads
- Enable **Windows Authentication** (the app uses `Trusted_Connection=yes`)
- Ensure SQL Server is running as `localhost` (default instance)

### 4. ODBC Driver 17 for SQL Server

- **Microsoft ODBC Driver 17 for SQL Server**
- Download: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
- Verify installation in Windows: Settings → Apps → search for "ODBC Driver 17"

### 5. Ollama (Optional — for AI-powered PDF extraction)

- **Ollama** — local LLM runtime (free, runs on your machine)
- Download: https://ollama.com/
- After installing, pull the required model:
  ```bash
  ollama pull qwen3:4b-q4_K_M
  ```
- Start the Ollama service:
  ```bash
  ollama serve
  ```
- Ollama runs on `http://127.0.0.1:11434` by default
- **If Ollama is not running**, the system automatically falls back to regex-based PDF extraction

### 6. Node.js (required by Playwright)

- **Node.js 18+** — needed for Playwright browser automation
- Download: https://nodejs.org/

### 7. Git

- For cloning this repository
- Download: https://git-scm.com/

---

## Python Package Installation

Create a virtual environment and install all required packages:

```bash
# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

# Install all packages (from requirements.txt)
pip install -r requirements.txt
```

Or install individually:

```bash
pip install pyodbc playwright openpyxl Pillow pypdf
```

### Package Summary

| Package | Version | Purpose |
|---------|---------|---------|
| `pyodbc` | 5.1+ | Connect to SQL Server (insert, query, update invoice data) |
| `playwright` | 1.40+ | Headless Chromium browser automation for MyInvois Portal form submission |
| `openpyxl` | 3.1+ | Read/write Excel template — fill cells, embed images, set alignment |
| `Pillow` | 10.0+ | Image processing — resize QR code images before embedding in Excel |
| `pypdf` | 4.0+ | Extract selectable text from PDF invoices |

### Standard Library (no install needed)

These are part of Python's standard library (already included):

| Module | Purpose |
|--------|---------|
| `http.server` | `ThreadingHTTPServer` — concurrent web server |
| `urllib.request` | Download QR code images from URLs |
| `json` | Parse Ollama AI responses, JSON API endpoints |
| `re` | Regex-based PDF text parsing (fallback extractor) |
| `decimal` | Precise money calculations (SST, totals) |
| `threading` | Background automation thread |
| `datetime` | Date/time formatting |
| `tempfile` | Temp files for QR code images |
| `io` | In-memory Excel byte streams |
| `pathlib` | Cross-platform file paths |
| `html` | HTML escaping for web GUI |

---

## Database Setup

The system uses **two databases** in the same SQL Server instance. A complete setup script with sample data is included in `setup_database.sql`.

### Option 1: Run the Setup Script (Recommended)

Open SQL Server Management Studio (SSMS) and run:

```sql
-- Execute the entire setup_database.sql file
-- This creates both databases, tables, and 10 sample invoices
```

Or via command line:

```cmd
sqlcmd -S localhost -E -i setup_database.sql
```

### Option 2: Manual Setup

### Database 1: `CompanyInvoiceDB`

Stores all invoice data (16 columns).

```sql
CREATE DATABASE CompanyInvoiceDB;
GO
USE CompanyInvoiceDB;
GO

CREATE TABLE dbo.Invoices (
    InvoiceId        INT IDENTITY(1,1) PRIMARY KEY,
    InvoiceNumber    NVARCHAR(50)  NOT NULL,
    SupplierName     NVARCHAR(200) NOT NULL,
    SupplierTIN      NVARCHAR(20)  NOT NULL,
    SupplierAddress  NVARCHAR(500) NULL,
    SupplierContact  NVARCHAR(300) NULL,
    BuyerName        NVARCHAR(200) NOT NULL,
    BuyerTIN         NVARCHAR(20)  NULL,
    Mykad            NVARCHAR(20)  NULL,
    BuyerAddress     NVARCHAR(500) NULL,
    BuyerContact     NVARCHAR(300) NULL,
    InvoiceDate      DATE          NOT NULL,
    InvoiceTime      TIME          NOT NULL,
    Subtotal         DECIMAL(12,2) NOT NULL,
    SSTAmount        DECIMAL(12,2) NOT NULL,
    TotalPayable     DECIMAL(12,2) NOT NULL
);
GO
```

### Database 2: `MyInvoisPortal`

Stores submission status, UUID, QR code URL, and verification URL.

```sql
CREATE DATABASE MyInvoisPortal;
GO
USE MyInvoisPortal;
GO

CREATE TABLE dbo.InvoiceInfo (
    InvoiceId    INT PRIMARY KEY,        -- Matches CompanyInvoiceDB.Invoices.InvoiceId
    Status       NVARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending | submitted | failed
    UUID         NVARCHAR(100) NULL,
    QRUrl        NVARCHAR(500) NULL,
    VerifyUrl    NVARCHAR(500) NULL,
    ErrorReason  NVARCHAR(500) NULL,
    SubmittedAt  DATETIME NULL
);
GO
```

### Cross-Database JOIN

The system uses SQL Server 3-part names to JOIN across databases:

```sql
SELECT i.*, ii.Status, ii.UUID, ii.QRUrl, ii.VerifyUrl
FROM CompanyInvoiceDB.dbo.Invoices i
INNER JOIN MyInvoisPortal.dbo.InvoiceInfo ii ON ii.InvoiceId = i.InvoiceId
```

### Verify Database Connection

```bash
python -c "import pyodbc; conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=CompanyInvoiceDB;Trusted_Connection=yes;TrustServerCertificate=yes;'); print('Connected!'); conn.close()"
```

---

## AI Model Setup (Ollama)

The system uses **Ollama** with the **Qwen3 4B** model for AI-powered PDF extraction. This is optional — if Ollama is not running, the system falls back to regex-based parsing.

### Step 1: Install Ollama

Download from https://ollama.com/ and install.

### Step 2: Pull the Model

```bash
ollama pull qwen3:4b-q4_K_M
```

This downloads a ~2.5 GB quantized model that runs locally on CPU or GPU.

### Step 3: Start Ollama Service

```bash
ollama serve
```

Ollama listens on `http://127.0.0.1:11434`.

### Step 4: Verify

```bash
curl http://127.0.0.1:11434/api/tags
```

Should return JSON with model list including `qwen3:4b-q4_K_M`.

### How AI Extraction Works

1. PDF text is extracted using `pypdf`
2. The full text is sent to Ollama with a JSON schema describing all invoice fields
3. Ollama returns structured JSON with extracted values
4. The system normalizes the data (MyKad format, money values, etc.)
5. If Ollama fails or is unavailable, regex-based `parse_invoice_from_text()` is used

### AI Schema

The system sends this schema to Ollama:

```json
{
  "invoice_number": "string | null",
  "supplier_tin": "string | null",
  "supplier_name": "string | null",
  "buyer_name": "string | null",
  "buyer_tin": "string | null",
  "buyer_mykad": "string | null",
  "invoice_date_time": "string | null",
  "items": [{"description": "...", "quantity": 1, "unit_price": 100, "line_total": 100}],
  "subtotal": 0,
  "sst_amount": 0,
  "total_payable": 0,
  "supplier_address": "string | null",
  "supplier_contact": "string | null",
  "buyer_address": "string | null",
  "buyer_contact": "string | null"
}
```

---

## Playwright Browser Setup

Playwright is used to automate form submission to the MyInvois Portal (Google Apps Script web app).

### Install Playwright Browsers

After `pip install playwright`, install the Chromium browser binary:

```bash
python -m playwright install chromium
```

This downloads a headless Chromium browser (~130 MB).

### Verify Installation

```bash
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
```

### How Playwright is Used

1. A headless Chromium browser is launched
2. For each valid (pending) invoice, the browser:
   - Navigates to the Google Apps Script form URL
   - Finds the form iframe
   - Fills 9 fields: Invoice Number, Supplier TIN, Buyer Name, Buyer TIN, MyKad, Date, Time, Total, SST
   - Clicks the submit button
   - Waits for the result element to appear
   - Extracts UUID, Verify URL, and QR code URL from the response
3. Results are written back to the `MyInvoisPortal.dbo.InvoiceInfo` table
4. The browser closes after processing all invoices

---

## Excel Template Setup

The system fills a pre-formatted Excel template with invoice data and embeds QR codes.

### Template File

Place the template at:

```
C:\Users\<YourUsername>\Downloads\SmartInvoice_AI_Invoice_Template.xlsx
```

Or update `TEMPLATE_PATH` in `invoice_excel_generator.py` to point to your template location.

### Template Structure

The template sheet is named **"Invoice Template"** and has this layout:

| Row | Column A (Label) | Column B-E (Data) | Merged |
|-----|-------------------|--------------------|----|
| 1 | INVOICE (title) | — | A1:E1 |
| 4 | SELLER DETAILS | INVOICE DETAILS | A4:C4, D4:E4 |
| 5 | Company Name | B5 (Supplier Name) | B5:C5 |
| 6 | Supplier Address | B6 | B6:C6 |
| 7 | Supplier Email / Phone | B7 | B7:C7 |
| 8 | Supplier TIN | B8 | B8:C8 |
| 10 | BILL TO / BUYER DETAILS | — | A10:E10 |
| 11 | Customer Name | B11 (Buyer Name) | B11:E11 |
| 12 | Buyer Address | B12 | B12:E12 |
| 13 | MyKad | B13 | B13:E13 |
| 14 | Buyer Email / Phone | B14 | (not merged) |
| 15 | Buyer TIN | B15 | B15:E15 |
| 17 | No. | Description / Qty / Unit Price / Amount | — |
| 18 | 1 | Item line 1 | — |
| 19-22 | 2-5 | Item lines 2-5 (cleared if unused) | — |
| 24 | Payment terms | Subtotal (RM) | E24 =SUM(E18:E22) |
| 25 | — | Discount (RM) | E25 |
| 26 | Bank details | Tax (RM) | E26 |
| 27 | — | Other charges (RM) | E27 |
| 28 | — | Invoice Total (RM) | E28 =E24-E25+E26+E27 |

### Column Widths

| Column | Width | Purpose |
|--------|-------|---------|
| A | 26.1 | Labels |
| B | 35.0 | Primary data |
| C | 12.0 | Merged with B |
| D | 18.0 | Unit Price / Summary labels |
| E | 20.0 | Invoice details / Amounts |
| F | 4.0 | Spacer (set at runtime) |
| G | 28.0 | QR code area (set at runtime) |

---

## Google Apps Script (MyInvois Portal Simulator)

This is our link to our MyInvois Portal(Demo Only) https://script.google.com/macros/s/AKfycbzzTAgAtgrMhqCVU3r2O1jToX8hJ0GhowKMajO44cMKQJCIex5r0pYhck0yNr52XyWX/exec

The system submits invoices to a **Google Apps Script Web App** that simulates the MyInvois Portal.

### What the Apps Script Does

1. Receives form data (9 fields) via HTTP POST
2. Generates a UUID (`Utilities.getUuid()`)
3. Creates a QR code URL pointing to a verification page
4. Returns UUID, QR URL, and Verify URL as HTML

### Form Fields

The form has these input elements (by DOM ID):

| ID | Field | Example |
|----|-------|---------|
| `#invNo` | Invoice Number | INV-2026-0004 |
| `#supplierTin` | Supplier TIN | C2023456702 |
| `#buyerName` | Buyer Name | Mutiara Retail Sdn Bhd |
| `#buyerTin` | Buyer TIN | C3011122201 |
| `#buyerMykad` | MyKad | 981022-48-0165 |
| `#invDate` | Invoice Date | 2026-09-08 |
| `#invTime` | Invoice Time | 12:54:00 |
| `#total` | Total Payable | 6335.06 |
| `#sst` | SST Amount | 469.26 |

### Result Elements

After submission, the form displays:

| ID | Content |
|----|---------|
| `#uuid` | Generated UUID |
| `#vurl` | Verification URL |
| `#qr` | QR code image (img src) |
| `#result` | Result container (visibility triggers extraction) |

### Deploy Your Own Apps Script

1. Go to https://script.google.com → New Project
2. Create a web app that:
   - Accepts the 9 form fields
   - Generates a UUID
   - Creates a QR code URL (e.g., using `api.qrserver.com`)
   - Returns HTML with `#uuid`, `#vurl`, `#qr`, and `#result` elements
3. Deploy as Web App (Execute as: Me, Access: Anyone)
4. Copy the deployment URL
5. Update `FORM_URL` in `invoice_web_gui.py`

---

## File Structure

```
0130am/
├── invoice_web_gui.py               # Main web server (HTTP + automation + HTML dashboard)
├── pdf_to_db.py                     # PDF extraction (Ollama AI + regex fallback) + DB insertion
├── check_invoices.py                # Validation layer — enforces TIN, MyKad, contact, SST rules
├── invoice_excel_generator.py       # Excel invoice generation from DB data + QR embedding
├── generate_sample_pdf.py           # Generate 3-page sample PDF invoices for testing
├── SmartInvoice_Template_3pages.pdf # Pre-generated sample PDF (3 invoices)
├── START_INVOICE_AUTO.bat           # Windows auto-restart watchdog launcher
├── setup_database.sql               # SQL setup script — creates both databases + 10 sample invoices
├── requirements.txt                 # Python package dependencies (pip install -r requirements.txt)
└── README.md                        # This file
```

### File Dependencies

```
invoice_web_gui.py
    ├── imports check_invoices.py       (validation)
    ├── imports pdf_to_db.py            (PDF upload + extraction)
    └── imports invoice_excel_generator.py  (Excel generation)

pdf_to_db.py
    └── imports pypdf                   (PDF text extraction)
    └── calls Ollama API (HTTP)         (AI extraction)

check_invoices.py
    └── standalone (no sibling imports)

invoice_excel_generator.py
    └── standalone (queries DB directly)

generate_sample_pdf.py
    └── standalone (writes raw PDF bytes, no external library)
```

---

## Configuration Reference

All configuration is hardcoded at the top of each Python file. Update these values for your environment.

### `invoice_web_gui.py`

```python
SQL_SERVER = "localhost"
SQL_DRIVER = "ODBC Driver 17 for SQL Server"
DATABASE = "CompanyInvoiceDB"       # Invoice data database
PORTAL_DB = "MyInvoisPortal"        # Submission status database
FORM_URL = "https://script.google.com/macros/s/AKfycbz.../exec"  # Google Apps Script URL
PORT = 8765                          # Web server port
```

### `pdf_to_db.py`

```python
SQL_SERVER = "localhost"
SQL_DRIVER = "ODBC Driver 17 for SQL Server"
DATABASE = "CompanyInvoiceDB"
PORTAL_DB = "MyInvoisPortal"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
OLLAMA_MODEL = "qwen3:4b-q4_K_M"
```

### `check_invoices.py`

```python
SERVER = "localhost"
DATABASE = "CompanyInvoiceDB"
PORTAL_DB = "MyInvoisPortal"
DRIVER = "ODBC Driver 17 for SQL Server"
SST_RATE = Decimal("0.08")     # 8% SST
TOLERANCE = Decimal("0.01")    # Amount tolerance
```

### `invoice_excel_generator.py`

```python
SQL_SERVER = "localhost"
SQL_DRIVER = "ODBC Driver 17 for SQL Server"
DATABASE = "CompanyInvoiceDB"
PORTAL_DB = "MyInvoisPortal"
TEMPLATE_PATH = r"C:\Users\<Username>\Downloads\SmartInvoice_AI_Invoice_Template.xlsx"
```

---

## How to Run

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/SmartInvoice-AI.git
cd SmartInvoice-AI

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/macOS

# 3. Install Python packages
pip install -r requirements.txt

# 4. Install Playwright Chromium browser
python -m playwright install chromium

# 5. (Optional) Install & start Ollama for AI extraction
#    Download from https://ollama.com/
ollama pull qwen3:4b-q4_K_M
ollama serve

# 6. Set up databases — run the SQL setup script in SSMS or:
sqlcmd -S localhost -E -i setup_database.sql
#    This creates CompanyInvoiceDB + MyInvoisPortal with 10 sample invoices

# 7. Deploy the MyInvois Portal simulator
#    a. Go to https://script.google.com → New Project
#    b. Create a web app that accepts 9 form fields, generates UUID + QR URL
#    c. Deploy as Web App (Execute as: Me, Access: Anyone)
#    d. Copy the URL and update FORM_URL in invoice_web_gui.py

# 8. Place Excel template at the configured path
#    Default: C:\Users\<YourUsername>\Downloads\SmartInvoice_AI_Invoice_Template.xlsx

# 9. Generate sample PDF invoices for testing (optional)
python generate_sample_pdf.py

# 10. Start the web server
python invoice_web_gui.py

# 11. Open browser → http://localhost:8765
```

### Using the Web GUI

1. **Upload PDF Invoices**: Go to `http://localhost:8765/upload`, select a PDF, click "Process"
2. **View All Invoices**: The home page (`/`) shows a table of all invoices with status badges
3. **Submit to Portal**: Go to `/submit`, click "SUBMIT INVOICES" — this validates and submits all pending invoices
4. **View QR Code**: Click "View QR" on any submitted invoice to see the QR code and UUID
5. **Generate Excel**: Click "Generate Invoice" on any submitted invoice to download the Excel file
6. **Check Status**: The `/status` endpoint returns JSON with automation progress

### Using the Auto-Restart Watchdog (Windows)

```bash
# Double-click or run in command prompt:
START_INVOICE_AUTO.bat
```

This launches the web server with auto-restart: if the server crashes, it restarts after 3 seconds.

---

## Web GUI Endpoints

### GET Endpoints

| Path | Type | Description |
|------|------|-------------|
| `/` | HTML | Data table — all invoices with status, actions, and stats |
| `/submit` | HTML | Submit page — one-click submission button, live logs, QR links |
| `/upload` | HTML | PDF upload page — file picker + process button + data preview |
| `/qr?id=N` | HTML | QR viewer page — invoice details, QR image, UUID |
| `/status` | JSON | Automation status — running, done, success, failed, pending, logs |
| `/all-invoices` | JSON | All invoices with all fields |
| `/submitted` | JSON | Submitted invoices only (with UUID, QR, Verify URL) |
| `/failed` | JSON | Failed invoices with ErrorReason |
| `/generate-invoice?id=N` | XLSX | Download generated Excel invoice for InvoiceId=N |

### POST Endpoints

| Path | Type | Description |
|------|------|-------------|
| `/start` | JSON | Start automation thread (validates + submits pending invoices) |
| `/pdf-process` | JSON | Upload PDF file (multipart/form-data), extract data, insert to DB |

---

## Data Formats & Validation Rules

### Supplier TIN (Company Tax Identification Number)

- **Format**: `C` followed by exactly 10 digits (e.g., `C2023456702`)
- **Regex**: `^C\d{10}$`
- **Required**: Yes (cannot be empty)
- **Used in**: Supplier TIN field (B8)

### Buyer TIN (Company Tax Identification Number)

- **Format**: `C` followed by exactly 10 digits (e.g., `C3011122201`)
- **Regex**: `^C\d{10}$`
- **Required**: Yes (cannot be empty)
- **Used in**: Buyer TIN field (B15)

### MyKad (Malaysian National ID)

- **Required format**: `XXXXXX-XX-XXXX` (6-2-4 format, 12 digits with dashes)
- **Example**: `981022-48-0165`
- **Regex**: `^\d{6}-\d{2}-\d{4}$`
- **Format breakdown**: YYMMDD-XX-XXXX (birth date - state code - serial number)

**Accepted input formats (auto-normalized):**

| Input | Normalized To |
|-------|---------------|
| `981022480165` (12 digits, no dashes) | `981022-48-0165` |
| `981022-48-165` (6-2-3, 11 digits) | `981022-48-0165` (padded) |
| `981022-48-0165` (already correct) | `981022-48-0165` (unchanged) |

**Validation**: Only the 6-2-4 format (`^\d{6}-\d{2}-\d{4}$`) passes validation. All other formats are rejected.

### Contact Information (Email / Phone)

- **Format**: Email address OR phone number, or both separated by pipe `|`
- **Examples**:
  - `billing@smartsolutions.my` (email only)
  - `03-21456789` (phone only)
  - `03-21456789 | billing@smartsolutions.my` (combined)
- **Email regex**: `^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$`
- **Phone regex**: `^[+]?[\d\s\-()]{7,}$` (7+ digits, allows spaces, dashes, parentheses, +)

### SST (Sales & Service Tax)

- **Rate**: 8% (`Decimal("0.08")`)
- **Validation**: `|Subtotal * 0.08 - SSTAmount| <= 0.01` (1 cent tolerance)
- **Formula**: `TotalPayable = Subtotal + SSTAmount` (no discount or other charges in DB)

### Invoice Number Uniqueness

- Duplicate invoice numbers are detected during validation
- Only the first occurrence (lowest InvoiceId) is allowed to proceed
- Duplicates are marked as `failed` with reason `"Duplicate invoice number"`

---

## PDF Extraction Pipeline

### Flow

```
PDF File
  │
  ▼
extract_pdf_text()        ← pypdf extracts selectable text from all pages
  │
  ├─ If Ollama is running ──► extract_with_ai()
  │                              │
  │                              ▼
  │                        Send text + JSON schema to Ollama
  │                        Parse JSON response
  │                        Normalize MyKad + money values
  │                              │
  │                              ▼
  │                        process_pdf() returns result
  │
  └─ If Ollama not running ──► extract_with_regex()
                                 │
                                 ▼
                           parse_invoice_from_text()
                           Uses _get_field() with 3 patterns:
                             A: Colon separator  ("Label: value")
                             B: Newline separator ("Label\nvalue")
                             C: Whitespace separator with known-label stop points
                           Uses _get_field_after() for buyer fields
                           (searches only after "BILL TO" marker)
                           _extract_mykad() normalizes MyKad format
                           _money() strips "(RM)" suffixes
                                 │
                                 ▼
                           process_pdf() returns result
```

### Regex Field Extraction Patterns

The regex fallback parser supports three extraction patterns:

**Pattern A — Colon separator:**
```
Company Name: Kota Digital Solutions Sdn Bhd
```

**Pattern B — Newline separator:**
```
Supplier Address
12 Jalan Bukit Bintang, 55100 Kuala Lumpur
```

**Pattern C — Whitespace separator with stop points:**
```
Company Name  Kota Digital Solutions Sdn Bhd  Supplier Address
              ↑ value starts after label    ↑ stops at next known label
```

`KNOWN_FIELD_LABELS` contains 30+ known labels used as stop points in Pattern C.

### Buyer-Specific Extraction

Buyer fields are extracted using `_get_field_after()`, which only searches text **after** the "BILL TO" marker to avoid matching supplier data.

---

## Excel Cell Mapping

The `invoice_excel_generator.py` fills the Excel template with these cell mappings:

### Seller Details (Rows 5-8)

| Cell | Merged | DB Field | Template Label |
|------|--------|----------|----------------|
| B5 | B5:C5 | SupplierName | Company Name |
| B6 | B6:C6 | SupplierAddress | Supplier Address |
| B7 | B7:C7 | SupplierContact | Supplier Email / Phone |
| B8 | B8:C8 | SupplierTIN | Supplier TIN |

### Invoice Details (Column E)

| Cell | DB Field | Template Label |
|------|----------|----------------|
| E5 | InvoiceNumber | Invoice No. |
| E6 | InvoiceDate (YYYY-MM-DD) | Invoice Date |
| E7 | InvoiceTime (HH:MM:SS) | Time |

### Buyer Details (Rows 11-15)

| Cell | Merged | DB Field | Template Label |
|------|--------|----------|----------------|
| B11 | B11:E11 | BuyerName | Customer Name |
| B12 | B12:E12 | BuyerAddress | Buyer Address |
| B13 | B13:E13 | Mykad | MyKad |
| B14 | — (B14 only) | BuyerContact | Buyer Email / Phone |
| B15 | B15:E15 | BuyerTIN | Buyer TIN |

### Item Table (Row 18)

| Cell | Value |
|------|-------|
| A18 | 1 (item number) |
| B18 | "Invoice total amount" (description) |
| C18 | 1 (quantity) |
| D18 | Subtotal (unit price = total amount) |
| E18 | `=C18*D18` (formula, kept from template) |

Rows 19-22 are cleared (set to None).

### Summary (Rows 24-28)

| Cell | Value | Template Label |
|------|-------|----------------|
| E24 | `=SUM(E18:E22)` (formula, kept) | Subtotal (RM) |
| E25 | 0 | Discount (RM) |
| E26 | SSTAmount from DB | Tax (RM) |
| E27 | 0 | Other charges (RM) |
| E28 | `=E24-E25+E26+E27` (formula, kept) | Invoice Total (RM) |

### QR Code & UUID (Column G)

| Cell | Content |
|------|---------|
| G2 | "Scan to Verify" (bold label) |
| G4 | QR code image (200x200 px, embedded) |
| G17 | "Validation UUID:" (label) |
| G18 | UUID value from DB |

Column F is set to width 4 (spacer), Column G to width 28.

### Alignment & Row Heights

- All data cells have `wrap_text=True` and `vertical="top"` alignment
- Row heights are auto-calculated based on text length and merged-cell widths
- Minimum row height: 20 points
- Line height: 15 points per line

---

## Auto-Restart Watchdog

`START_INVOICE_AUTO.bat` is a Windows batch file that:

1. Launches `invoice_web_gui.py` using `start /wait`
2. If the Python process exits (crash or Ctrl+C), waits 3 seconds
3. Restarts the server automatically
4. Loops forever until you press Ctrl+C twice

### Usage

```cmd
:: Double-click START_INVOICE_AUTO.bat
:: Or run from command prompt:
START_INVOICE_AUTO.bat
```

### To Stop

- Press **Ctrl+C** twice in the command prompt window
- Or close the command prompt window

### Python Path

The bat file uses this Python path by default:

```cmd
%USERPROFILE%\.workbuddy-ai\binaries\python\envs\default\Scripts\python.exe
```

Update this line to match your Python installation if needed:

```cmd
set "PYTHON_EXE=python"
```

---

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| `pyodbc.InterfaceError: Cannot connect to data source` | Ensure SQL Server is running and ODBC Driver 17 is installed |
| `pyodbc.IntegrityError: Cannot insert NULL into column 'BuyerTIN'` | Make the column nullable: `ALTER TABLE dbo.Invoices ALTER COLUMN BuyerTIN nvarchar(20) NULL` |
| Playwright `Executable doesn't exist` | Run `python -m playwright install chromium` |
| Ollama not detected | Run `ollama serve` and verify `http://127.0.0.1:11434/api/tags` responds |
| Excel template not found | Update `TEMPLATE_PATH` in `invoice_excel_generator.py` |
| PDF extraction returns no text | The PDF may be scanned (image-only). Use OCR or ensure the PDF has selectable text |
| Form submission timeout | Check that `FORM_URL` points to a valid Google Apps Script web app |
| Port 8765 already in use | Change `PORT` in `invoice_web_gui.py` |
| MyKad validation fails | Ensure MyKad is in `XXXXXX-XX-XXXX` (6-2-4) format |

### Verify Each Component

```bash
# 1. Python version
python --version  # Should be 3.10+

# 2. SQL Server connection
python -c "import pyodbc; conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=CompanyInvoiceDB;Trusted_Connection=yes;TrustServerCertificate=yes;'); print('SQL Server OK'); conn.close()"

# 3. Ollama
curl http://127.0.0.1:11434/api/tags

# 4. Playwright
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"

# 5. Excel packages
python -c "from openpyxl import load_workbook; from PIL import Image; print('Excel packages OK')"

# 6. PDF extraction
python -c "from pypdf import PdfReader; print('pypdf OK')"
```

---

## License

This is a demo/educational project. Verify all fields, tax treatment, and totals before real-world use.

---

## Disclaimer

This system simulates the MyInvois Portal using a Google Apps Script web app. It is not an official LHDN (Lembaga Hasil Dalam Negeri) e-Invoice submission system. All data is for demonstration purposes only.
