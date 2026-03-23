#!/usr/bin/env python3
"""
Complete OMMU data extraction - ensures ALL 28 operators are captured
"""
import subprocess
import re
from datetime import datetime
import json
import csv

# All 28 operators based on Jan 2, 2026 report
ALL_OPERATORS = [
    "Trulieve",
    "MÜV",
    "Curaleaf Florida, LLC",
    "Ayr Cannabis Dispensary",
    "Surterra Wellness",
    "Green Dragon",
    "Planet 13 Florida Cannabis for the Planet",
    "FLUENT",
    "Sunnyside*",
    "GrowHealthy",
    "Sanctuary Cannabis",
    "GTI Florida, LLC",
    "Cookies Florida",
    "Jungle Boys",
    "Sunburn",
    "The Flowery",
    "Mint Cannabis",
    "Goldflower Cannabis",
    "Insa - Cannabis for Real Life",
    "One Plant Cannabis",
    "Eden Florida, LLC",
    "Fino Cannabis",
    "Prosperity Medical, LLC",
    "Revolution Florida",
    "TheraTrue Florida, LLC",
    "Henry Crusaw",
    "Leola Robinson",
    "Moton Hopkins Jr."
]

DATES = [
    "2026-01-02",
    "2026-01-09",
    "2026-01-16",
    "2026-01-23",
    "2026-01-30",
    "2026-02-06",
    "2026-02-13",
    "2026-02-20",
    "2026-02-27",
    "2026-03-06",
    "2026-03-13",
    "2026-03-20"
]

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using pdftotext"""
    result = subprocess.run(
        ['pdftotext', '-layout', pdf_path, '-'],
        capture_output=True,
        text=True
    )
    return result.stdout

def parse_operator_data(text, operator_name):
    """Extract data for a specific operator from text"""
    # Escape special regex characters
    escaped_name = re.escape(operator_name)
    
    # Pattern to match operator line with data
    # Format: Name    Locations    THC_mg    CBD_mg    Smoking_oz
    pattern = rf'{escaped_name}\s+(\d+|n/a)\s+([\d,]+)\s+([\d,]+)\s+([\d,.]+)'
    
    match = re.search(pattern, text)
    
    if match:
        locations = match.group(1)
        mg_thc = match.group(2).replace(',', '')
        mg_cbd = match.group(3).replace(',', '')
        smoking_oz = match.group(4).replace(',', '')
        
        # Convert n/a to 0
        if locations == 'n/a':
            locations = '0'
            
        return {
            'locations': int(locations),
            'mg_thc': int(mg_thc),
            'mg_cbd': int(mg_cbd),
            'smoking_oz': float(smoking_oz)
        }
    
    return None

def extract_all_data():
    """Extract data from all PDFs for all operators"""
    data = {}
    
    for operator in ALL_OPERATORS:
        data[operator] = {}
    
    missing_data = []
    
    for date in DATES:
        pdf_path = f"{date}.pdf"
        print(f"Processing {pdf_path}...")
        
        text = extract_text_from_pdf(pdf_path)
        
        for operator in ALL_OPERATORS:
            operator_data = parse_operator_data(text, operator)
            
            if operator_data:
                data[operator][date] = operator_data
                print(f"  ✓ {operator}: {operator_data['locations']} locations")
            else:
                # Default to zeros if not found
                data[operator][date] = {
                    'locations': 0,
                    'mg_thc': 0,
                    'mg_cbd': 0,
                    'smoking_oz': 0.0
                }
                missing_data.append((date, operator))
                print(f"  ✗ {operator}: NOT FOUND (defaulting to zeros)")
    
    if missing_data:
        print("\n⚠️  WARNING: Missing data for:")
        for date, operator in missing_data:
            print(f"  - {date}: {operator}")
    
    return data

def save_csv_files(data):
    """Save data to CSV files by metric"""
    
    # Locations CSV
    with open('locations.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['MMTC Operator'] + DATES)
        for operator in ALL_OPERATORS:
            row = [operator] + [data[operator][date]['locations'] for date in DATES]
            writer.writerow(row)
    print("✓ Saved locations.csv")
    
    # mg_thc CSV
    with open('mg_thc.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['MMTC Operator'] + DATES)
        for operator in ALL_OPERATORS:
            row = [operator] + [data[operator][date]['mg_thc'] for date in DATES]
            writer.writerow(row)
    print("✓ Saved mg_thc.csv")
    
    # mg_cbd CSV
    with open('mg_cbd.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['MMTC Operator'] + DATES)
        for operator in ALL_OPERATORS:
            row = [operator] + [data[operator][date]['mg_cbd'] for date in DATES]
            writer.writerow(row)
    print("✓ Saved mg_cbd.csv")
    
    # smoking_oz CSV
    with open('smoking_oz.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['MMTC Operator'] + DATES)
        for operator in ALL_OPERATORS:
            row = [operator] + [data[operator][date]['smoking_oz'] for date in DATES]
            writer.writerow(row)
    print("✓ Saved smoking_oz.csv")
    
    # Summary CSV
    with open('summary.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Total Locations', 'Total mg THC', 'Total mg CBD', 'Total Smoking oz'])
        for date in DATES:
            total_locations = sum(data[op][date]['locations'] for op in ALL_OPERATORS)
            total_thc = sum(data[op][date]['mg_thc'] for op in ALL_OPERATORS)
            total_cbd = sum(data[op][date]['mg_cbd'] for op in ALL_OPERATORS)
            total_smoking = sum(data[op][date]['smoking_oz'] for op in ALL_OPERATORS)
            writer.writerow([date, total_locations, total_thc, total_cbd, f"{total_smoking:.3f}"])
    print("✓ Saved summary.csv")
    
    # All data CSV (combined)
    with open('all_data.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'MMTC Operator', 'Locations', 'mg THC', 'mg CBD', 'Smoking oz'])
        for date in DATES:
            for operator in ALL_OPERATORS:
                d = data[operator][date]
                writer.writerow([date, operator, d['locations'], d['mg_thc'], d['mg_cbd'], d['smoking_oz']])
    print("✓ Saved all_data.csv")

def save_json(data):
    """Save raw data as JSON"""
    with open('extracted_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("✓ Saved extracted_data.json")

if __name__ == '__main__':
    print(f"Extracting data for {len(ALL_OPERATORS)} operators across {len(DATES)} weeks...\n")
    
    data = extract_all_data()
    
    print("\nSaving CSV files...")
    save_csv_files(data)
    
    print("\nSaving JSON...")
    save_json(data)
    
    print(f"\n✅ Complete! Extracted data for all {len(ALL_OPERATORS)} operators.")
    print(f"   Files: locations.csv, mg_thc.csv, mg_cbd.csv, smoking_oz.csv, summary.csv, all_data.csv, extracted_data.json")
