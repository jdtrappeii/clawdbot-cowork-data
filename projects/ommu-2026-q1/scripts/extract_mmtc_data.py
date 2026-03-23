#!/usr/bin/env python3
"""
Extract MMTC operator performance data from Florida OMMU weekly reports
and compile into Excel comparison spreadsheet.
"""

import subprocess
import re
import pandas as pd
from datetime import datetime
import os

# List of PDF files in chronological order
pdf_files = [
    ('2026-01-02.pdf', '2026-01-02'),
    ('2026-01-09.pdf', '2026-01-09'),
    ('2026-01-16.pdf', '2026-01-16'),
    ('2026-01-23.pdf', '2026-01-23'),
    ('2026-01-30.pdf', '2026-01-30'),
    ('2026-02-06.pdf', '2026-02-06'),
    ('2026-02-13.pdf', '2026-02-13'),
    ('2026-02-20.pdf', '2026-02-20'),
    ('2026-02-27.pdf', '2026-02-27'),
    ('2026-03-06.pdf', '2026-03-06'),
    ('2026-03-13.pdf', '2026-03-13'),
    ('2026-03-20.pdf', '2026-03-20'),
]

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using pdftotext."""
    try:
        result = subprocess.run(['pdftotext', pdf_path, '-'], 
                              capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error extracting {pdf_path}: {e}")
        return ""

def parse_mmtc_data(text):
    """Parse MMTC dispensation data from extracted PDF text."""
    data = []
    
    # Look for the table section
    lines = text.split('\n')
    in_table = False
    
    for i, line in enumerate(lines):
        # Find the start of the MMTC table
        if 'MMTC Name' in line:
            in_table = True
            continue
        
        if not in_table:
            continue
        
        # Skip header rows
        if 'Dispensing' in line or 'Locations' in line or 'Medical Marijuana' in line:
            continue
        if 'Low-THC Cannabis' in line or 'Marijuana in a Form' in line:
            continue
        if '(mg THC)' in line or '(mg CBD)' in line or 'for Smoking (oz)' in line:
            continue
        
        # Stop at footnotes or next section
        if line.strip().startswith('*') or line.strip().startswith('Total') or \
           'For MMTC contact' in line or len(line.strip()) == 0:
            if data:  # Only break if we've collected some data
                break
        
        # Try to parse MMTC data line
        # Format: MMTC Name | Locations | mg THC | mg CBD | oz Smoking
        # The name might span multiple words
        
        # Look for lines with numeric data
        # Match pattern: name followed by numbers
        match = re.search(r'^(.+?)\s+(\d+)\s+([\d,]+)\s+([\d,]+)\s+([\d,.]+)\s*$', line.strip())
        if match:
            name = match.group(1).strip()
            locations = int(match.group(2))
            mg_thc = int(match.group(3).replace(',', ''))
            mg_cbd = int(match.group(4).replace(',', ''))
            oz_smoking = float(match.group(5).replace(',', ''))
            
            data.append({
                'MMTC Name': name,
                'Dispensing Locations': locations,
                'Medical Marijuana (mg THC)': mg_thc,
                'Low-THC Cannabis (mg CBD)': mg_cbd,
                'Smoking (oz)': oz_smoking
            })
    
    return data

def clean_number(val):
    """Clean and convert numeric values."""
    if pd.isna(val) or val == '':
        return 0
    if isinstance(val, (int, float)):
        return val
    # Remove commas and convert
    return float(str(val).replace(',', ''))

# Main extraction
all_data = {}

print("Extracting data from PDFs...")
for pdf_file, date in pdf_files:
    print(f"Processing {pdf_file}...")
    pdf_path = os.path.join('/root/.clawdbot/workspace/ommu_reports_2026_q1', pdf_file)
    text = extract_text_from_pdf(pdf_path)
    
    if not text:
        print(f"  WARNING: No text extracted from {pdf_file}")
        continue
    
    mmtc_data = parse_mmtc_data(text)
    
    if mmtc_data:
        print(f"  Found {len(mmtc_data)} MMTC operators")
        all_data[date] = mmtc_data
    else:
        print(f"  WARNING: No MMTC data found in {pdf_file}")

# Create Excel workbook with multiple sheets
print("\nCreating Excel workbook...")
excel_path = '/root/.clawdbot/workspace/FL_MMTC_Q1_2026_Comparison.xlsx'

with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    
    # Sheet 1: Dispensing Locations Comparison
    print("Creating Dispensing Locations sheet...")
    locations_data = {}
    for date, operators in all_data.items():
        locations_data[date] = {op['MMTC Name']: op['Dispensing Locations'] 
                               for op in operators}
    
    df_locations = pd.DataFrame(locations_data).fillna(0).astype(int)
    df_locations = df_locations.sort_index()  # Sort by operator name
    df_locations.to_excel(writer, sheet_name='Dispensing Locations')
    
    # Sheet 2: Medical Marijuana (mg THC) Comparison
    print("Creating Medical Marijuana (mg THC) sheet...")
    thc_data = {}
    for date, operators in all_data.items():
        thc_data[date] = {op['MMTC Name']: op['Medical Marijuana (mg THC)'] 
                         for op in operators}
    
    df_thc = pd.DataFrame(thc_data).fillna(0).astype(int)
    df_thc = df_thc.sort_index()
    df_thc.to_excel(writer, sheet_name='Medical Marijuana (mg THC)')
    
    # Sheet 3: Low-THC Cannabis (mg CBD) Comparison
    print("Creating Low-THC Cannabis (mg CBD) sheet...")
    cbd_data = {}
    for date, operators in all_data.items():
        cbd_data[date] = {op['MMTC Name']: op['Low-THC Cannabis (mg CBD)'] 
                         for op in operators}
    
    df_cbd = pd.DataFrame(cbd_data).fillna(0).astype(int)
    df_cbd = df_cbd.sort_index()
    df_cbd.to_excel(writer, sheet_name='Low-THC Cannabis (mg CBD)')
    
    # Sheet 4: Smoking (oz) Comparison
    print("Creating Smoking (oz) sheet...")
    smoking_data = {}
    for date, operators in all_data.items():
        smoking_data[date] = {op['MMTC Name']: op['Smoking (oz)'] 
                             for op in operators}
    
    df_smoking = pd.DataFrame(smoking_data).fillna(0)
    df_smoking = df_smoking.sort_index()
    df_smoking.to_excel(writer, sheet_name='Smoking (oz)')
    
    # Sheet 5: Summary Statistics
    print("Creating Summary Statistics sheet...")
    summary_stats = []
    
    for date in sorted(all_data.keys()):
        operators = all_data[date]
        total_locations = sum(op['Dispensing Locations'] for op in operators)
        total_thc = sum(op['Medical Marijuana (mg THC)'] for op in operators)
        total_cbd = sum(op['Low-THC Cannabis (mg CBD)'] for op in operators)
        total_smoking = sum(op['Smoking (oz)'] for op in operators)
        num_operators = len(operators)
        
        summary_stats.append({
            'Week Ending': date,
            'Total Operators': num_operators,
            'Total Dispensing Locations': total_locations,
            'Total Medical Marijuana (mg THC)': total_thc,
            'Total Low-THC Cannabis (mg CBD)': total_cbd,
            'Total Smoking (oz)': round(total_smoking, 2),
            'Avg Locations per Operator': round(total_locations / num_operators, 1) if num_operators > 0 else 0,
            'Avg THC per Operator (mg)': round(total_thc / num_operators, 0) if num_operators > 0 else 0
        })
    
    df_summary = pd.DataFrame(summary_stats)
    df_summary.to_excel(writer, sheet_name='Summary Statistics', index=False)
    
    # Sheet 6: All Data Combined
    print("Creating All Data Combined sheet...")
    combined_data = []
    
    for date in sorted(all_data.keys()):
        for operator in all_data[date]:
            row = {'Week Ending': date}
            row.update(operator)
            combined_data.append(row)
    
    df_combined = pd.DataFrame(combined_data)
    df_combined.to_excel(writer, sheet_name='All Data Combined', index=False)

print(f"\n✓ Excel file created successfully: {excel_path}")
print(f"  Total weeks processed: {len(all_data)}")
print(f"  Total sheets: 6")
print("  - Dispensing Locations (side-by-side comparison)")
print("  - Medical Marijuana (mg THC) (side-by-side comparison)")
print("  - Low-THC Cannabis (mg CBD) (side-by-side comparison)")
print("  - Smoking (oz) (side-by-side comparison)")
print("  - Summary Statistics")
print("  - All Data Combined")
