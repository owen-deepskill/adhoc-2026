#!/usr/bin/env python3
"""
Convert subtitle_final.yaml to XLSX format with columns:
start, end, text_en, text_ko, edit, caption, shorts

Required packages:
    pip install pyyaml pandas openpyxl
"""

import sys
from pathlib import Path

# Check for required packages
try:
    import yaml
except ImportError:
    print("Error: pyyaml is not installed. Install it with: pip install pyyaml")
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    print("Error: pandas is not installed. Install it with: pip install pandas")
    sys.exit(1)

try:
    import openpyxl
except ImportError:
    print("Error: openpyxl is not installed. Install it with: pip install openpyxl")
    sys.exit(1)


def convert_yaml_to_xlsx(yaml_path, xlsx_path):
    """
    Convert YAML subtitle file to XLSX format.
    
    Args:
        yaml_path: Path to input YAML file
        xlsx_path: Path to output XLSX file
    """
    try:
        # Read YAML file
        print(f"Reading YAML file: {yaml_path}")
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data:
            print("Error: YAML file is empty or invalid")
            return False
        
        # Prepare list of dictionaries for DataFrame
        rows = []
        for entry in data:
            # Handle shorts: convert to string if it's a number, empty string if not present
            shorts_value = entry.get('shorts', '')
            if shorts_value != '':
                shorts_value = str(shorts_value)
            
            row = {
                'start': entry.get('start', ''),
                'end': entry.get('end', ''),
                'text_en': entry.get('text_en', ''),
                'text_ko': entry.get('text_ko', ''),
                'edit': entry.get('edit', ''),
                'caption': entry.get('caption', ''),
                'shorts': shorts_value
            }
            rows.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(rows)
        
        # Reorder columns to match requested order
        column_order = ['start', 'end', 'text_en', 'text_ko', 'edit', 'caption', 'shorts']
        df = df[column_order]
        
        # Write to XLSX
        print(f"Writing to XLSX file: {xlsx_path}")
        df.to_excel(xlsx_path, index=False, engine='openpyxl')
        
        print(f"Successfully converted {len(df)} rows to {xlsx_path}")
        return True
        
    except FileNotFoundError:
        print(f"Error: File not found: {yaml_path}")
        return False
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # Set paths
    script_dir = Path(__file__).parent
    yaml_file = script_dir / 'subtitle_final.yaml'
    xlsx_file = script_dir / 'subtitle_final.xlsx'
    
    # Convert
    success = convert_yaml_to_xlsx(yaml_file, xlsx_file)
    sys.exit(0 if success else 1)
