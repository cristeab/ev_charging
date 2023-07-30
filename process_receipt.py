#!/usr/bin/env python3

from PIL import Image
import PyPDF2
import io
import re
import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import calendar


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
        return float(total_ron)
    return 0

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

    dates = []
    total_cost_kwh = []
    cost_per_kwh = []
    total_cost_ron = []

    for file in os.listdir(pdf_folder_path):
        file_path = os.path.join(pdf_folder_path, file)
        if os.path.isfile(file_path) and file.lower().endswith(".pdf"):

            extracted_text = extract_text_from_pdf(file_path)

            invoice_date = extract_invoice_date(extracted_text)
            datetime_date = datetime.strptime(invoice_date, "%d/%m/%Y")
            details = extract_kwh_details(extracted_text)[0]
            total_kwh = float(details[0])
            vat = extract_vat(extracted_text)
            price_per_kwh = round(float(details[1]) * (1 + vat / 100), 2)
            total_ron = extract_total_ron(extracted_text)

            dates.append(datetime_date)
            total_cost_kwh.append(total_kwh)
            cost_per_kwh.append(price_per_kwh)
            total_cost_ron.append(total_ron)

data_table = pd.DataFrame({
    'invoice date': dates,
    'total kWh': total_cost_kwh,
    'cost RON/kWh': cost_per_kwh,
    'total RON': total_cost_ron
})
data_table_sorted = data_table.sort_values(by='invoice date')

print(data_table_sorted)

# Extract year and month from 'invoice date' column and create new columns 'year' and 'month'
data_table_sorted['year'] = data_table_sorted['invoice date'].dt.year
data_table_sorted['month'] = data_table_sorted['invoice date'].dt.month

# Group data by year and month and sum the 'total RON' for each month
monthly_total_ron = data_table_sorted.groupby(['year', 'month'])['total RON'].sum()
monthly_total_kwh = data_table_sorted.groupby(['year', 'month'])['total kWh'].sum()

# Create a DataFrame with the grouped data
monthly_total_ron_df = monthly_total_ron.reset_index()
monthly_total_kwh_df = monthly_total_kwh.reset_index()

# Create a bar plot graph
plt.bar(monthly_total_ron_df['month'], monthly_total_ron_df['total RON'], label='RON')
plt.xlabel('Time')
plt.ylabel('Total')
plt.title('Total per Month')
plt.xticks(range(1, 13), calendar.month_abbr[1:13])  # To show month abbreviations on x-axis

plt.bar(monthly_total_kwh_df['month'], monthly_total_kwh_df['total kWh'], label='kWh')

# Annotate the bars with the total cost values
for x, y in zip(monthly_total_ron_df['month'], monthly_total_ron_df['total RON']):
    plt.text(x, y, str(round(y, 2)), ha='center', va='bottom')

for x, y in zip(monthly_total_kwh_df['month'], monthly_total_kwh_df['total kWh']):
    plt.text(x, y, str(round(y, 2)), ha='center', va='bottom', color='white')

plt.legend()

plt.show()
