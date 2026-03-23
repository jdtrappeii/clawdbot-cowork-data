# OMMU Reports 2026 Q1

Florida Office of Medical Marijuana Use (OMMU) weekly reports for Q1 2026.

## Overview

Weekly data extracted from OMMU PDF reports covering 12 weeks (January 2 - March 20, 2026).

**Metrics tracked:**
- Dispensary location counts
- THC milligrams sold
- CBD milligrams sold  
- Smoking products (ounces) sold

**Operators:** 24 licensed cannabis dispensaries in Florida

## Data Files (`/data`)

| File | Description |
|------|-------------|
| `locations.csv` | Dispensary location counts by operator & week |
| `mg_thc.csv` | THC milligrams sold by operator & week |
| `mg_cbd.csv` | CBD milligrams sold by operator & week |
| `smoking_oz.csv` | Smoking product ounces sold by operator & week |
| `summary.csv` | Aggregate statistics across all operators |
| `all_data.csv` | Combined dataset (all metrics) |
| `extracted_data.json` | Raw extracted data in JSON format |

## Scripts (`/scripts`)

- `extract_data_simple.py` - Main PDF extraction script
- `extract_mmtc_data.py` - Alternative extraction approach
- `csv_to_xlsx_manual.py` - CSV to Excel converter
- `create_excel.py` - Excel workbook generator

## Data Structure

Each CSV follows this format:
```
MMTC Operator,2026-01-02,2026-01-09,2026-01-16,...
Operator Name,value,value,value,...
```

## Top Operators (by locations)

1. **Trulieve** - 162-165 locations
2. **MÜV** - 82-84 locations
3. **Curaleaf** - 69-70 locations
4. **Ayr Cannabis** - 64-66 locations
5. **Surterra Wellness** - 45 locations

## Usage

**Analysis Ideas:**
- Market share trends
- Growth rates by operator
- THC vs CBD sales patterns
- Geographic expansion tracking

**For Claude:**
- Reference files via GitHub raw URLs
- Import CSVs for visualization
- Time series analysis
- Competitive analysis

## Source

Data extracted from official OMMU weekly reports (PDFs available in original directory).

---

**Last Updated:** 2026-03-23  
**Status:** Active - Q1 complete, ready for analysis
