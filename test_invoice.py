#!/usr/bin/env python3

from PIL import Image
import PyPDF2
import re
import os


# file_path = '/Users/bogdan/Documents/Auto/MB_GLE/FacturiIncarcare/23EXWFA00057094_1223.pdf'
file_path = '/Users/bogdan/Documents/Auto/MB_GLE/FacturiIncarcare/23EXWFA00058604_1223.pdf'

def extract_text_from_pdf(pdf_path):
    text = ""
    pdf_file = open(pdf_path, 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file)

    for page_num in range(0, len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        image = page.extract_text()  # Extract text from the PDF page as an image
        text += image + "\n"

    pdf_file.close()
    return text

def extract_subscription_type(text):
    pattern = r'(Basic X|Premium X|Quick Recharge)\s+RON\s+\d+\.\d{2}'
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None

extracted_text = extract_text_from_pdf(file_path)
subcription = extract_subscription_type(extracted_text)
print(subcription)