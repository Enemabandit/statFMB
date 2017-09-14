from xhtml2pdf import pisa
from io import StringIO

def create_pdf(pdf_data):
    pdf = StringIO()
    pisa.CreatePDF(StringIO(pdf_data.encode('utf-8')), pdf)
    return pdf
