# JSON JSONL Fixer - Quick Reference Guide

## What This Script Does
Automatically fixes common JSON errors in line-delimited JSON (JSONL) files:
- Triple quotes in arrays (`"""` → `""`)
- Malformed HTML attributes (`"rowspan="2""` → `"rowspan=2"`)
- Unescaped quotes in HTML content within the "gt" field

## How to Use with New Data

### Method 1: Command Line (Recommended)
```bash
# Fix a new file
python fix_json_complete.py path/to/your/newdata.txt

# Specify custom output filename
python fix_json_complete.py newdata.txt newdata_clean.txt

# Fix multiple files in a loop
for file in data/*.txt; do
    python fix_json_complete.py "$file"
done
```

### Method 2: Interactive Mode
```bash
# Run without arguments
python fix_json_complete.py

# Then enter your file path when prompted
```

### Method 3: Use as a Python Module
```python
from fix_json_complete import process_jsonl_file

# Fix a file programmatically
success = process_jsonl_file('my_data.txt', 'my_data_fixed.txt')

if success:
    print("All lines fixed!")
```

## Output Files
- **`filename_fixed.txt`** - Contains all valid/fixed JSON lines
- **`filename_backup.txt`** - Created only if you choose to replace the original

## Common Workflows

### New Training Data
```bash
python fix_json_complete.py aws-to-paddle-dataset/train_new.txt
# Creates: train_new_fixed.txt
```

### Batch Processing
```powershell
# PowerShell
Get-ChildItem -Path data -Filter *.txt | ForEach-Object {
    python fix_json_complete.py $_.FullName
}
```

### Validation Only (Don't Replace)
```bash
python fix_json_complete.py myfile.txt
# When prompted "Replace original? (y/n):" → type 'n'
# Your original stays safe, use myfile_fixed.txt
```

## Tips
- ✅ Always run on new data before training
- ✅ The script creates backups automatically when replacing
- ✅ Invalid lines are dropped (not fixable) - check the summary
- ✅ Works with UTF-8 encoded files
- ⚠️ If many lines are dropped, manually inspect the original data

## Script Location
`c:\Users\Anurag Katkar\Documents\Programs\Work\aws-textract\fix_json_complete.py`
