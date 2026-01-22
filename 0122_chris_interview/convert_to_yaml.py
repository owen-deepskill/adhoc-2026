import csv
import yaml
from pathlib import Path

# Read CSV file
csv_file = Path(__file__).parent / 'subtitle_en.csv'
yaml_file = Path(__file__).parent / 'subtitle_reviewed.yaml'

subtitle_data = []

with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        subtitle_entry = {
            'start': row['Start Time'].strip(),
            'end': row['End Time'].strip(),
            'text': row['Text'].strip()
        }
        subtitle_data.append(subtitle_entry)

# Write to YAML file
with open(yaml_file, 'w', encoding='utf-8') as f:
    yaml.dump(subtitle_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

print(f"Successfully converted {len(subtitle_data)} subtitle entries to {yaml_file}")
