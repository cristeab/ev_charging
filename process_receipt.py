#!/usr/bin/env python3

from PIL import Image
import PyPDF2
import io
import re
import os


# Function to extract text from a PDF using OCR
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

def extract_total_ron(text):
    # Pattern to match TOTAL: RON <amount>
    pattern_total_ron = r"TOTAL:\s*RON\s*(\d+\.\d{2})"
    match_total = re.search(pattern_total_ron, text)
    if match_total:
        total_ron = match_total.group(1)
        return total_ron
    return None

def extract_invoice_date(text):
    # Pattern to match Invoice date: <date>
    pattern_invoice_date = r"Invoice date:\s*(\d{2}/\d{2}/\d{4})"
    match_date = re.search(pattern_invoice_date, text)
    if match_date:
        invoice_date = match_date.group(1)
        return invoice_date
    return None

def extract_kwh_details(text):
    # Pattern to match <date> <kWh> kWh x RON <price>/kWh RON <total_price>
    pattern_kwh_details = r"(\d+\.\d{2})\s+kWh\s+x\s+RON\s+(\d+\.\d+)\s*/kWh\s+RON\s+(\d+\.\d{2})"
    matches_kwh = re.findall(pattern_kwh_details, text)
    kwh_list = []
    for match in matches_kwh:
        kwh, price_per_kwh, total_price = match
        kwh_list.append((kwh, price_per_kwh, total_price))
    return kwh_list

def extract_vat(text):
    # Pattern to match VAT RON <amount>
    pattern_vat_percent = r"VAT\s+RON\s+\d+\.\d+\s+(\d+)%"
    match_vat = re.search(pattern_vat_percent, text)
    if match_vat:
        vat_amount = match_vat.group(1)
        return int(vat_amount)
    return 0

if __name__ == "__main__":
    # path to your PDF file
    pdf_folder_path = '/Users/bogdan/Documents/MB_GLE/FacturiIncarcare'

    for file in os.listdir(pdf_folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path) and file.lower().endswith(".pdf"):

            extracted_text = extract_text_from_pdf(file_path)
            print(extracted_text)

            total_ron = extract_total_ron(extracted_text)
            invoice_date = extract_invoice_date(extracted_text)
            vat = extract_vat(extracted_text)
            details = extract_kwh_details(extracted_text)[0]
            energy_kwh = float(details[0])
            price_per_kwh = round(float(details[1]) * (1 + vat / 100), 2)
            print(f"{invoice_date}: {energy_kwh} kWh x {price_per_kwh} RON/kWh = {total_ron} RON")

