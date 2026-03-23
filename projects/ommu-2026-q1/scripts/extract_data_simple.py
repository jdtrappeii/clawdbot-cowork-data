#!/usr/bin/env python3
"""
Extract MMTC operator performance data from Florida OMMU weekly reports.
Simple version using CSV output, no pandas dependency.
"""

import subprocess
import re
import csv
import json
from collections import defaultdict

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
    """Extract text from PDF using pdftotext with layout preservation."""
    try:
        result = subprocess.run(['pdftotext', '-layout', pdf_path, '-'], 
                              capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error extracting {pdf_path}: {e}")
        return ""

def clean_number(s):
    """Clean numeric string - remove commas, handle n/a."""
    s = s.strip()
    if s in ('n/a', 'N/A', '', '-'):
        return '0'
    return s.replace(',', '')

def parse_mmtc_data(text):
    """Parse MMTC dispensation data from extracted PDF text."""
    data = []
    lines = text.split('\n')
    
    # Find the table start
    table_start = -1
    for i, line in enumerate(lines):
        if 'MMTC Dispensations for' in line:
            table_start = i
            break
    
    if table_start == -1:
        print("  Could not find MMTC Dispensations table")
        return data
    
    # Process lines after table header
    in_data = False
    for i in range(table_start, len(lines)):
        line = lines[i]
        
        # Skip header rows
        if 'MMTC Name' in line or 'Dispensing' in line or 'Locations' in line:
            in_data = True
            continue
        if 'Medical Marijuana' in line or 'Low-THC' in line or 'mg THC' in line:
            continue
        if 'mg CBD' in line or 'for Smoking' in line:
            continue
        
        # Stop at table continuation or end markers
        if 'Table continued' in line or 'Total' in line:
            break
        if 'General Background' in line:
            break
        
        if not in_data:
            continue
        
        # Skip empty lines
        if len(line.strip()) < 10:
            continue
        
        # Parse the line - layout format:
        # NAME (left-aligned) ... LOCATIONS ... MG_THC ... MG_CBD ... SMOKING_OZ
        # Try to extract columns using spacing
        
        # Remove leading/trailing whitespace
        line = line.rstrip()
        
        # Skip lines that look like footnotes
        if line.strip().startswith('*'):
            continue
        
        # Match pattern: name followed by numeric columns
        # The layout has significant spacing between columns
        parts = line.split()
        
        if len(parts) < 4:
            continue
        
        # Try to find where numbers start
        # Look for first number that could be locations (should be reasonable)
        num_start_idx = -1
        for j, part in enumerate(parts):
            # Check if this could be a location count (0-200 range typically)
            try:
                val = int(part.replace(',', ''))
                if 0 <= val <= 500:  # Reasonable range for locations
                    num_start_idx = j
                    break
            except ValueError:
                continue
        
        if num_start_idx == -1 or num_start_idx < 1:
            continue
        
        # Name is everything before the numbers
        name = ' '.join(parts[:num_start_idx])
        
        # Skip if name looks like a header or invalid
        if name in ('MMTC Name', '') or 'Dispensing' in name:
            continue
        
        # Numbers are after the name
        numbers = parts[num_start_idx:]
        
        if len(numbers) < 4:
            continue
        
        try:
            locations = clean_number(numbers[0])
            mg_thc = clean_number(numbers[1])
            mg_cbd = clean_number(numbers[2])
            smoking_oz = clean_number(numbers[3])
            
            # Convert to appropriate types
            locations = int(locations)
            mg_thc = int(mg_thc)
            mg_cbd = int(mg_cbd)
            smoking_oz = float(smoking_oz)
            
            data.append({
                'MMTC Name': name,
                'Dispensing Locations': locations,
                'Medical Marijuana (mg THC)': mg_thc,
                'Low-THC Cannabis (mg CBD)': mg_cbd,
                'Smoking (oz)': smoking_oz
            })
            
        except (ValueError, IndexError) as e:
            # Skip lines that don't parse correctly
            continue
    
    return data

# Main extraction
all_data = {}

print("Extracting data from PDFs...")
for pdf_file, date in pdf_files:
    print(f"Processing {pdf_file}...")
    pdf_path = f'/root/.clawdbot/workspace/ommu_reports_2026_q1/{pdf_file}'
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

# Save to JSON for inspection
with open('/root/.clawdbot/workspace/ommu_reports_2026_q1/extracted_data.json', 'w') as f:
    json.dump(all_data, f, indent=2)

print(f"\n✓ Data extracted to JSON: extracted_data.json")
print(f"  Total weeks processed: {len(all_data)}")

# Get all unique operator names
all_operators = set()
for date_data in all_data.values():
    for op in date_data:
        all_operators.add(op['MMTC Name'])

all_operators = sorted(all_operators)
print(f"  Total unique operators: {len(all_operators)}")

# Create CSV files for each metric
dates = sorted(all_data.keys())

# 1. Dispensing Locations
with open('/root/.clawdbot/workspace/ommu_reports_2026_q1/locations.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['MMTC Operator'] + dates)
    
    for operator in all_operators:
        row = [operator]
        for date in dates:
            # Find this operator in this date's data
            value = 0
            for op_data in all_data.get(date, []):
                if op_data['MMTC Name'] == operator:
                    value = op_data['Dispensing Locations']
                    break
            row.append(value)
        writer.writerow(row)

# 2. Medical Marijuana (mg THC)
with open('/root/.clawdbot/workspace/ommu_reports_2026_q1/mg_thc.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['MMTC Operator'] + dates)
    
    for operator in all_operators:
        row = [operator]
        for date in dates:
            value = 0
            for op_data in all_data.get(date, []):
                if op_data['MMTC Name'] == operator:
                    value = op_data['Medical Marijuana (mg THC)']
                    break
            row.append(value)
        writer.writerow(row)

# 3. Low-THC Cannabis (mg CBD)
with open('/root/.clawdbot/workspace/ommu_reports_2026_q1/mg_cbd.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['MMTC Operator'] + dates)
    
    for operator in all_operators:
        row = [operator]
        for date in dates:
            value = 0
            for op_data in all_data.get(date, []):
                if op_data['MMTC Name'] == operator:
                    value = op_data['Low-THC Cannabis (mg CBD)']
                    break
            row.append(value)
        writer.writerow(row)

# 4. Smoking (oz)
with open('/root/.clawdbot/workspace/ommu_reports_2026_q1/smoking_oz.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['MMTC Operator'] + dates)
    
    for operator in all_operators:
        row = [operator]
        for date in dates:
            value = 0.0
            for op_data in all_data.get(date, []):
                if op_data['MMTC Name'] == operator:
                    value = op_data['Smoking (oz)']
                    break
            row.append(value)
        writer.writerow(row)

# 5. Summary statistics
with open('/root/.clawdbot/workspace/ommu_reports_2026_q1/summary.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Week Ending', 'Total Operators', 'Total Locations', 
                     'Total mg THC', 'Total mg CBD', 'Total Smoking (oz)',
                     'Avg Locations/Operator', 'Avg mg THC/Operator'])
    
    for date in dates:
        operators = all_data[date]
        total_locs = sum(op['Dispensing Locations'] for op in operators)
        total_thc = sum(op['Medical Marijuana (mg THC)'] for op in operators)
        total_cbd = sum(op['Low-THC Cannabis (mg CBD)'] for op in operators)
        total_smoking = sum(op['Smoking (oz)'] for op in operators)
        num_ops = len(operators)
        
        avg_locs = round(total_locs / num_ops, 1) if num_ops > 0 else 0
        avg_thc = round(total_thc / num_ops, 0) if num_ops > 0 else 0
        
        writer.writerow([date, num_ops, total_locs, total_thc, total_cbd,
                        round(total_smoking, 2), avg_locs, int(avg_thc)])

# 6. All data combined
with open('/root/.clawdbot/workspace/ommu_reports_2026_q1/all_data.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Week Ending', 'MMTC Name', 'Dispensing Locations',
                     'Medical Marijuana (mg THC)', 'Low-THC Cannabis (mg CBD)',
                     'Smoking (oz)'])
    
    for date in dates:
        for op in all_data[date]:
            writer.writerow([date, op['MMTC Name'], op['Dispensing Locations'],
                           op['Medical Marijuana (mg THC)'], 
                           op['Low-THC Cannabis (mg CBD)'],
                           op['Smoking (oz)']])

print("\n✓ Created CSV files:")
print("  - locations.csv")
print("  - mg_thc.csv")
print("  - mg_cbd.csv")
print("  - smoking_oz.csv")
print("  - summary.csv")
print("  - all_data.csv")
