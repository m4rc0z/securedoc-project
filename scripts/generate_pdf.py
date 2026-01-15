from reportlab.pdfgen import canvas

def create_pdf(filename):
    c = canvas.Canvas(filename)
    c.drawString(100, 750, "CONFIDENTIAL DOCUMENT")
    c.drawString(100, 700, "Subject: Personal Information")
    c.drawString(100, 650, "Name: Max Mustermann")
    c.drawString(100, 600, "Date of birth: 12.01.1991")
    c.drawString(100, 550, "Address: Musterstrasse 1, 12345 Musterstadt")
    c.save()

if __name__ == "__main__":
    create_pdf("test_document_1991.pdf")
    print("PDF created: test_document_1991.pdf")
