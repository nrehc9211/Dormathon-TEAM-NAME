"""
Generate a 3-page sample PDF that matches the SmartInvoice AI Excel Template layout.

Template structure (from SmartInvoice_AI_Invoice_Template.xlsx):
  - INVOICE header + disclaimer
  - SELLER DETAILS: Company Name, Address, Business Registration No., Supplier TIN, Email/Phone
  - INVOICE DETAILS: Invoice No., Invoice Date (yyyy-mm-dd), Invoice Time (hh:mm:ss), Currency
  - BILL TO / BUYER DETAILS: Customer Name, Address, Business / Tax ID, Email/Phone
  - Item table: No. | Description | Qty | Unit Price (RM) | Amount (RM) — 3 line items
  - Payment terms + Bank details
  - Summary: Subtotal (RM), Discount (RM), Tax (RM), Other charges (RM), Invoice Total (RM)
  - Disclaimer

Each page = one invoice with different data.
Date format: 2026-10-08 (YYYY-MM-DD)
Time format: 15:31:00 (HH:MM:SS)

Output: SmartInvoice_Template_3pages.pdf
"""
from pathlib import Path

# ---- 3 different invoices (different data from template) --------------------
INVOICES = [
    {
        # Seller
        "company_name": "Tekun Maju Resources Sdn Bhd",
        "address": "45 Jalan Industri, Kawasan Perindustrian, 81200 Johor Bahru, Johor",
        "business_reg": "202005012345",
        "supplier_tin": "C2020050123",
        "email_phone": "07-2345678 | sales@tekunmaju.my",
        # Invoice
        "invoice_number": "INV-2026-0101",
        "invoice_date": "2026-10-08",
        "invoice_time": "09:15:30",
        "currency": "MYR (RM)",
        # Buyer
        "customer_name": "Nurul Aisyah binti Mohd",
        "buyer_address": "88 Jalan Merdeka, 80000 Johor Bahru, Johor",
        "buyer_taxid": "950614145678",
        "buyer_email": "aisyah.mohd@email.com",
        # Items
        "items": [
            ("1", "A4 Paper 80gsm (5 reams)", "5", "25.00", "125.00"),
            ("2", "Toner Cartridge HP 88A (1 unit)", "1", "180.00", "180.00"),
            ("3", "Binding Service (1 lot)", "1", "45.00", "45.00"),
        ],
        # Summary
        "subtotal": "350.00",
        "discount": "0.00",
        "tax": "28.00",
        "other_charges": "0.00",
        "total": "378.00",
        # Bank
        "bank_details": "Bank details (optional): RHB Bank | Account: 212-0012345",
    },
    {
        "company_name": "Mega Print Solutions Sdn Bhd",
        "address": "23 Jalan Teknologi, Bandar Utama, 47800 Petaling Jaya, Selangor",
        "business_reg": "201901009888",
        "supplier_tin": "C2019010098",
        "email_phone": "03-78901234 | info@megaprint.my",
        "invoice_number": "INV-2026-0102",
        "invoice_date": "2026-10-08",
        "invoice_time": "14:22:00",
        "currency": "MYR (RM)",
        "customer_name": "Tan Wei Ming",
        "buyer_address": "12 Jalan SS2/72, 47300 Petaling Jaya, Selangor",
        "buyer_taxid": "910228071234",
        "buyer_email": "weiming.tan@email.com",
        "items": [
            ("1", "Banner Printing PVC (3 pieces)", "3", "85.00", "255.00"),
            ("2", "Business Cards 350gsm (500 pcs)", "1", "120.00", "120.00"),
            ("3", "Lamination A4 (10 sheets)", "10", "8.00", "80.00"),
        ],
        "subtotal": "455.00",
        "discount": "0.00",
        "tax": "36.40",
        "other_charges": "0.00",
        "total": "491.40",
        "bank_details": "Bank details (optional): Maybank | Account: 564-7890123",
    },
    {
        "company_name": "Sentosa Hardware Trading Sdn Bhd",
        "address": "67 Jalan Besi, Taman Industri, 53300 Kuala Lumpur",
        "business_reg": "201705006777",
        "supplier_tin": "C2017050067",
        "email_phone": "03-42876543 | sales@sentosahw.my",
        "invoice_number": "INV-2026-0103",
        "invoice_date": "2026-10-08",
        "invoice_time": "16:45:00",
        "currency": "MYR (RM)",
        "customer_name": "Rajeswary a/p Subramaniam",
        "buyer_address": "15 Jalan Taman, 56000 Cheras, Kuala Lumpur",
        "buyer_taxid": "880315085678",
        "buyer_email": "rajes.subra@email.com",
        "items": [
            ("1", "Cordless Drill Machine (1 unit)", "1", "350.00", "350.00"),
            ("2", "Screw Driver Set (5 boxes)", "5", "28.00", "140.00"),
            ("3", "Safety Helmet (3 pieces)", "3", "45.00", "135.00"),
        ],
        "subtotal": "625.00",
        "discount": "0.00",
        "tax": "50.00",
        "other_charges": "0.00",
        "total": "675.00",
        "bank_details": "Bank details (optional): CIMB Bank | Account: 760-3456789",
    },
]


def _esc(text):
    """Escape special characters for PDF text string."""
    return str(text).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_content_stream(inv):
    """Build PDF content stream matching the Excel template layout."""
    lines = []

    # Header
    lines.append("INVOICE")
    lines.append("Editable sample template for SmartInvoice AI demo - not an official LHDN e-Invoice form")

    # Seller section
    lines.append("SELLER DETAILS")
    lines.append("Company Name")
    lines.append(inv["company_name"])
    lines.append("Address")
    lines.append(inv["address"])
    lines.append("Business Registration No.")
    lines.append(inv["business_reg"])
    lines.append("Supplier TIN")
    lines.append(inv["supplier_tin"])
    lines.append("Email / Phone")
    lines.append(inv["email_phone"])

    # Invoice details section
    lines.append("INVOICE DETAILS")
    lines.append("Invoice No.")
    lines.append(inv["invoice_number"])
    lines.append("Invoice Date")
    lines.append(inv["invoice_date"])
    lines.append("Invoice Time")
    lines.append(inv["invoice_time"])
    lines.append("Currency")
    lines.append(inv["currency"])

    # Bill to section
    lines.append("BILL TO / BUYER DETAILS")
    lines.append("Customer Name")
    lines.append(inv["customer_name"])
    lines.append("Address")
    lines.append(inv["buyer_address"])
    lines.append("Business / Tax ID (if applicable)")
    lines.append(inv["buyer_taxid"])
    lines.append("Email / Phone")
    lines.append(inv["buyer_email"])

    # Item table
    lines.append(" No.")
    lines.append(" Description")
    lines.append(" Qty")
    lines.append(" Unit Price (RM)")
    lines.append(" Amount (RM)")
    for item in inv["items"]:
        lines.append(item[0])               # No.
        lines.append(item[1])               # Description
        lines.append(" " + item[2])          # Qty
        lines.append(" " + item[3])          # Unit Price
        lines.append(" " + item[4])          # Amount

    # Footer
    lines.append("Payment terms: 14 days from invoice date.")
    lines.append(inv["bank_details"])

    # Summary section
    lines.append("Subtotal (RM)")
    lines.append(" RM " + inv["subtotal"])
    lines.append("Discount (RM)")
    lines.append(" RM " + inv["discount"])
    lines.append("Tax (RM)")
    lines.append(" RM " + inv["tax"])
    lines.append("Other charges (RM)")
    lines.append(" RM " + inv["other_charges"])
    lines.append("Invoice Total (RM)")
    lines.append(" RM " + inv["total"])

    # Disclaimer
    lines.append("Demo data only. Verify all fields, tax treatment and totals before real-world use.")

    # Build content stream
    parts = ["BT", "/F1 12 Tf", "50 750 Td"]
    first = True
    for line in lines:
        if not first:
            parts.append("0 -14 Td")
        first = False
        parts.append(f"({_esc(line)}) Tj")
    parts.append("ET")
    return "\n".join(parts)


def _build_pdf(invoices):
    """Build a multi-page PDF as raw bytes."""
    num_pages = len(invoices)
    page_kids = [f"{3 + 2 * i} 0 R" for i in range(num_pages)]

    objects = []
    objects.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    objects.append(
        f"2 0 obj\n<< /Type /Pages /Kids [{' '.join(page_kids)}] /Count {num_pages} >>\nendobj\n".encode()
    )

    for i, inv in enumerate(invoices):
        page_obj_num = 3 + 2 * i
        content_obj_num = 4 + 2 * i

        stream_text = _build_content_stream(inv)
        stream_bytes = stream_text.encode("latin-1")

        objects.append(
            f"{page_obj_num} 0 obj\n"
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Contents {content_obj_num} 0 R "
            f"/Resources << /Font << /F1 9 0 R >> >> >>\n"
            f"endobj\n".encode()
        )
        objects.append(
            f"{content_obj_num} 0 obj\n<< /Length {len(stream_bytes)} >>\nstream\n".encode()
            + stream_bytes
            + b"\nendstream\nendobj\n"
        )

    objects.append(
        b"9 0 obj\n"
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\n"
        b"endobj\n"
    )

    pdf = bytearray()
    pdf.extend(b"%PDF-1.4\n")

    offsets = []
    for obj in objects:
        offsets.append(len(pdf))
        pdf.extend(obj)

    xref_offset = len(pdf)
    pdf.extend(b"xref\n")
    pdf.extend(f"0 {len(objects) + 1}\n".encode())
    pdf.extend(b"0000000000 65535 f \n")
    for off in offsets:
        pdf.extend(f"{off:010d} 00000 n \n".encode())

    pdf.extend(b"trailer\n")
    pdf.extend(f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode())
    pdf.extend(b"startxref\n")
    pdf.extend(f"{xref_offset}\n".encode())
    pdf.extend(b"%%EOF\n")

    return bytes(pdf)


def main():
    output_path = Path(__file__).parent / "SmartInvoice_Template_3pages.pdf"
    pdf_bytes = _build_pdf(INVOICES)
    output_path.write_bytes(pdf_bytes)
    print(f"Generated: {output_path}")
    print(f"  Pages: {len(INVOICES)}")
    print(f"  Layout: matches Excel template (SmartInvoice_AI_Invoice_Template.xlsx)")
    print(f"  Date format: YYYY-MM-DD | Time format: HH:MM:SS")
    print(f"  File size: {len(pdf_bytes)} bytes")
    for i, inv in enumerate(INVOICES, 1):
        print(f"  Page {i}: {inv['invoice_number']} | {inv['company_name']} | "
              f"Date: {inv['invoice_date']} Time: {inv['invoice_time']} | "
              f"Total: RM {inv['total']}")


if __name__ == "__main__":
    main()
