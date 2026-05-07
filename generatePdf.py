from fpdf import FPDF
from cloudinaryUpload import upload_pdf
from datetime import datetime
import os

pdf= FPDF()

class ReceiptPDF(FPDF):

    def header(self):

        # ===== STORE NAME =====
        self.set_font("Arial", "B", 18)
        self.cell(0, 8, "HEWSTORE SYSTEM", ln=True, align="C")

        # ===== STORE DETAILS =====
        self.set_font("Arial", "", 10)
        self.cell(0, 5, "Nairobi, Kenya", ln=True, align="C")
        self.cell(0, 5, "Tel: +254 700 000000", ln=True, align="C")
        self.cell(0, 5, "Email: support@hewstore.com", ln=True, align="C")

        self.ln(3)

        # separator
        self.line(10, self.get_y(), 200, self.get_y())

        self.ln(5)

        # title
        self.set_font("Arial", "B", 12)
        self.cell(0, 8, "OFFICIAL SALES RECEIPT", ln=True, align="C")

        self.ln(3)

    def footer(self):

        self.set_y(-20)

        self.set_font("Arial", "I", 9)

        self.cell(
            0,
            5,
            "Thank you for shopping with HEWSTORE",
            align="C"
        )

        self.ln(5)

        self.cell(
            0,
            5,
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            align="C"
        )


def generate_pdf(data, filename):

    pdf = ReceiptPDF()

    # ===== PAGE SETTINGS =====
    pdf.set_auto_page_break(auto=True, margin=25)

    pdf.set_left_margin(10)
    pdf.set_right_margin(10)

    pdf.add_page()

    # =========================
    # RECEIPT INFO
    # =========================
    pdf.set_font("Arial", size=10)

    pdf.cell(100, 6, f"Receipt No: {data['receipt_no']}", ln=0)

    pdf.cell(
        0,
        6,
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        ln=1
    )

    pdf.ln(4)

    # =========================
    # CUSTOMER INFO
    # =========================
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, "CUSTOMER DETAILS", ln=True)

    pdf.set_font("Arial", "", 10)

    pdf.cell(0, 6, f"Customer Name: {data['customer_name']}", ln=True)
    pdf.cell(0, 6, f"Phone Number: {data['phone']}", ln=True)

    pdf.ln(5)

    # =========================
    # TABLE HEADER
    # =========================
    pdf.set_fill_color(230, 230, 230)

    pdf.set_font("Arial", "B", 10)

    pdf.cell(80, 8, "ITEM", border=1, fill=True)
    pdf.cell(25, 8, "QTY", border=1, fill=True, align="C")
    pdf.cell(40, 8, "PRICE", border=1, fill=True, align="C")
    pdf.cell(45, 8, "TOTAL", border=1, fill=True, align="C")

    pdf.ln()

    # =========================
    # ITEMS
    # =========================
    pdf.set_font("Arial", "", 10)

    subtotal = 0

    for item in data["items"]:

        total = item["qty"] * item["price"]
        subtotal += total

        # item name
        pdf.cell(80, 8, item["name"], border=1)

        # qty
        pdf.cell(25, 8, str(item["qty"]), border=1, align="C")

        # price
        pdf.cell(
            40,
            8,
            f"KES {item['price']:,.2f}",
            border=1,
            align="R"
        )

        # total
        pdf.cell(
            45,
            8,
            f"KES {total:,.2f}",
            border=1,
            align="R"
        )

        pdf.ln()

    # =========================
    # TOTALS
    # =========================
    vat = subtotal * 0.16
    grand_total = subtotal + vat

    pdf.ln(4)

    pdf.set_font("Arial", "", 10)

    pdf.cell(145, 8, "Subtotal", align="R")
    pdf.cell(45, 8, f"KES {subtotal:,.2f}", border=1, align="R")
    pdf.ln()

    pdf.cell(145, 8, "VAT (16%)", align="R")
    pdf.cell(45, 8, f"KES {vat:,.2f}", border=1, align="R")
    pdf.ln()

    pdf.set_font("Arial", "B", 12)

    pdf.cell(145, 10, "GRAND TOTAL", align="R")

    pdf.cell(
        45,
        10,
        f"KES {grand_total:,.2f}",
        border=1,
        align="R"
    )

    pdf.ln(15)

    # =========================
    # PAYMENT INFO
    # =========================
    pdf.set_font("Arial", "", 10)

    payment_method = data.get("payment_method", "Cash")

    pdf.cell(0, 6, f"Payment Method: {payment_method}", ln=True)

    pdf.ln(5)

    # =========================
    # BARCODE STYLE FOOTER
    # =========================
    pdf.set_font("Courier", "B", 12)

    pdf.cell(
        0,
        8,
        f"*{data['receipt_no']}*",
        ln=True,
        align="C"
    )

    # =========================
    # SAVE PDF
    # =========================
    import os

    os.makedirs("receipts", exist_ok=True)

    file_path = os.path.join("receipts", f"{filename}.pdf")

    pdf.output(file_path)

    print("PDF SAVED:", os.path.abspath(file_path))

    return file_path


# def generate_pdf(txt, filename):
#     print('my filename in generate pdf is', filename)
#     pdf.add_page()
#     pdf.set_font("Arial", size=12)
#     pdf.multi_cell(200, 10, txt=txt, align='C')
#     os.makedirs("receipts", exist_ok=True)
#     pdf.output(f"receipts/{filename}.pdf")
    
#     print(f"PDF generated and uploaded successfully as {filename}.pdf")
    
    # upload_pdf(filename)