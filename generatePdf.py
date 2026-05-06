from fpdf import FPDF
from cloudinaryUpload import upload_pdf
from datetime import datetime



pdf = FPDF()

# def generate_pdf(txt, filename):
#     print('my filename in generate pdf is', filename)
#     pdf.add_page()
#     pdf.set_font("Arial", size=12)
#     pdf.multi_cell(200, 10, txt=txt, align='C')
#     pdf.output(f"reciepts/{filename}.pdf")
    
#     print(f"PDF generated and uploaded successfully as {filename}.pdf")
    
#     upload_pdf(filename)

class ReceiptPDF(FPDF):

    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "HEWSTORE SYSTEM", ln=True, align="C")

        self.set_font("Arial", "", 10)
        self.cell(0, 6, "Official Sales Receipt", ln=True, align="C")

        self.ln(5)
        self.line(10, 30, 200, 30)  # separator line
        self.ln(5)


def generate_pdf(data, filename):

    pdf = ReceiptPDF()

    # ✅ Better margins
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)

    pdf.add_page()

    # ========================
    # RECEIPT INFO
    # ========================
    pdf.set_font("Arial", size=10)

    pdf.cell(100, 6, f"Receipt #: {data['receipt_no']}", ln=0)
    pdf.cell(0, 6, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=1)

    pdf.ln(3)

    # ========================
    # CUSTOMER INFO
    # ========================
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Customer Details", ln=True)

    pdf.set_font("Arial", size=10)
    pdf.cell(0, 6, f"Name: {data['customer_name']}", ln=True)
    pdf.cell(0, 6, f"Phone: {data['phone']}", ln=True)

    pdf.ln(5)

    # ========================
    # TABLE HEADER
    # ========================
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(220, 220, 220)

    pdf.cell(70, 8, "Item", border=1, fill=True)
    pdf.cell(30, 8, "Qty", border=1, fill=True, align="C")
    pdf.cell(40, 8, "Price", border=1, fill=True, align="C")
    pdf.cell(40, 8, "Total", border=1, fill=True, align="C")
    pdf.ln()

    # ========================
    # ITEMS
    # ========================
    pdf.set_font("Arial", size=10)

    total_amount = 0

    for item in data["items"]:

        total = item["qty"] * item["price"]
        total_amount += total

        pdf.cell(70, 8, item["name"], border=1)
        pdf.cell(30, 8, str(item["qty"]), border=1, align="C")
        pdf.cell(40, 8, f"{item['price']:.2f}", border=1, align="R")
        pdf.cell(40, 8, f"{total:.2f}", border=1, align="R")
        pdf.ln()

    # ========================
    # TOTAL SECTION
    # ========================
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(140, 10, "TOTAL AMOUNT", border=0)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(40, 10, f"KES {total_amount:.2f}", border=1, align="R")

    pdf.ln(10)

    # ========================
    # FOOTER
    # ========================
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, "Thank you for shopping with us!", ln=True, align="C")

    # ========================
    # SAVE
    # ========================
    file_path = f"receipts/{filename}.pdf"
    pdf.output(file_path)

    print(f"PDF generated: {file_path}")

    upload_pdf(filename)