#!/usr/bin/env python3
"""
Convert CSV files to XLSX using zipfile and XML (no dependencies).
Creates a minimal but valid Excel file.
"""

import csv
import zipfile
import os
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

def create_xlsx_from_csvs(csv_files, output_path):
    """Create XLSX file from multiple CSV files."""
    
    # Create temporary directory for Excel parts
    import tempfile
    import shutil
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create directory structure
        os.makedirs(os.path.join(temp_dir, '_rels'), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, 'docProps'), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, 'xl', '_rels'), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, 'xl', 'worksheets'), exist_ok=True)
        
        # [Content_Types].xml
        with open(os.path.join(temp_dir, '[Content_Types].xml'), 'w') as f:
            f.write('''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>''')
            for i in range(len(csv_files)):
                f.write(f'\n<Override PartName="/xl/worksheets/sheet{i+1}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>')
            f.write('\n</Types>')
        
        # _rels/.rels
        with open(os.path.join(temp_dir, '_rels', '.rels'), 'w') as f:
            f.write('''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>''')
        
        # docProps/core.xml
        with open(os.path.join(temp_dir, 'docProps', 'core.xml'), 'w') as f:
            f.write('''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<dc:creator>OMMU Data Extractor</dc:creator>
<dcterms:created xsi:type="dcterms:W3CDTF">2026-03-23T00:00:00Z</dcterms:created>
</cp:coreProperties>''')
        
        # docProps/app.xml
        with open(os.path.join(temp_dir, 'docProps', 'app.xml'), 'w') as f:
            f.write(f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">
<Application>Python XLSX Generator</Application>
<AppVersion>1.0</AppVersion>
<Company>Florida OMMU</Company>
<TotalTime>0</TotalTime>
</Properties>''')
        
        # xl/workbook.xml
        with open(os.path.join(temp_dir, 'xl', 'workbook.xml'), 'w') as f:
            f.write('''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets>''')
            for i, (sheet_name, _) in enumerate(csv_files, 1):
                f.write(f'\n<sheet name="{sheet_name}" sheetId="{i}" r:id="rId{i}"/>')
            f.write('\n</sheets>\n</workbook>')
        
        # xl/_rels/workbook.xml.rels
        with open(os.path.join(temp_dir, 'xl', '_rels', 'workbook.xml.rels'), 'w') as f:
            f.write('''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">''')
            for i in range(len(csv_files)):
                f.write(f'\n<Relationship Id="rId{i+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i+1}.xml"/>')
            f.write('\n</Relationships>')
        
        # Create worksheets from CSVs
        for i, (sheet_name, csv_path) in enumerate(csv_files, 1):
            with open(csv_path, 'r') as csvfile:
                reader = csv.reader(csvfile)
                rows = list(reader)
            
            with open(os.path.join(temp_dir, 'xl', 'worksheets', f'sheet{i}.xml'), 'w') as f:
                f.write('''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<sheetData>''')
                
                for row_idx, row in enumerate(rows, 1):
                    f.write(f'\n<row r="{row_idx}">')
                    for col_idx, cell_value in enumerate(row, 1):
                        col_letter = chr(64 + col_idx) if col_idx <= 26 else 'A' + chr(64 + col_idx - 26)
                        cell_ref = f'{col_letter}{row_idx}'
                        
                        # Try to determine if value is numeric
                        is_numeric = False
                        if row_idx > 1 and col_idx > 1:  # Not header, not first column
                            try:
                                float(cell_value)
                                is_numeric = True
                            except (ValueError, TypeError):
                                pass
                        
                        if is_numeric:
                            f.write(f'\n<c r="{cell_ref}"><v>{cell_value}</v></c>')
                        else:
                            # Escape XML special characters
                            escaped = str(cell_value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
                            f.write(f'\n<c r="{cell_ref}" t="inlineStr"><is><t>{escaped}</t></is></c>')
                    f.write('\n</row>')
                
                f.write('\n</sheetData>\n</worksheet>')
        
        # Create ZIP file (XLSX is just a ZIP with XML files)
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
        
        print(f"✓ Created Excel file: {output_path}")
        
    finally:
        shutil.rmtree(temp_dir)

# Define sheets
base_path = '/root/.clawdbot/workspace/ommu_reports_2026_q1/'
csv_files = [
    ('Dispensing Locations', base_path + 'locations.csv'),
    ('Medical Marijuana (mg THC)', base_path + 'mg_thc.csv'),
    ('Low-THC Cannabis (mg CBD)', base_path + 'mg_cbd.csv'),
    ('Smoking (oz)', base_path + 'smoking_oz.csv'),
    ('Summary Statistics', base_path + 'summary.csv'),
    ('All Data Combined', base_path + 'all_data.csv'),
]

output_path = '/root/.clawdbot/workspace/FL_MMTC_Q1_2026_Comparison.xlsx'

print("Creating Excel workbook from CSV files...")
create_xlsx_from_csvs(csv_files, output_path)
print(f"\n✓ Excel workbook created successfully!")
print(f"  Location: {output_path}")
print(f"  Total sheets: {len(csv_files)}")
for sheet_name, _ in csv_files:
    print(f"    - {sheet_name}")
