import requests
from io import BytesIO
import pdfplumber


def download_pdf(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BytesIO(response.content)
    except requests.exceptions.RequestException as e:
        return None


def extract_text_from_pdf(pdf_stream):
    try:
        with pdfplumber.open(pdf_stream) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        return None


def process_pdf_from_url(url):
    pdf_stream = download_pdf(url)
    if pdf_stream:
        text = extract_text_from_pdf(pdf_stream)
        if text:
            return text
        else:
            ''
    return ''


if __name__ == "__main__":
    url = "https://fpu-stg.branding-element.com/qa/9773/SEND_DOCUMENT_ATTACHMENT/48845_TestReport_Tejal_Mehta_1524011272_ff4bcb98_2075_4165_ae34_eaaca9b52829.pdf-BLCAb.pdf"
    extracted_text = process_pdf_from_url(url)
    if extracted_text:
        print(extracted_text)
    else:
        print("Failed to extract text from the PDF.")
