#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract shorts segments from subtitle_final.yaml
Groups entries by shorts number and displays Korean text
"""

import re
import sys
from collections import defaultdict

# Set UTF-8 encoding for output
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def parse_yaml_file(filepath):
    """Parse the YAML-like subtitle file and extract shorts segments"""
    shorts_data = defaultdict(list)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    current_entry = {}
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for start timestamp
        if line.startswith('- start:'):
            current_entry = {}
            current_entry['start'] = line.replace('- start:', '').strip()
        
        # Check for end timestamp
        elif line.startswith('end:'):
            current_entry['end'] = line.replace('end:', '').strip()
        
        # Check for English text
        elif line.startswith('text_en:'):
            current_entry['text_en'] = line.replace('text_en:', '').strip()
        
        # Check for Korean text
        elif line.startswith('text_ko:'):
            current_entry['text_ko'] = line.replace('text_ko:', '').strip()
        
        # Check for shorts label
        elif line.startswith('shorts:'):
            shorts_num = line.replace('shorts:', '').strip()
            if shorts_num and current_entry.get('text_ko'):
                shorts_data[int(shorts_num)].append({
                    'start': current_entry.get('start', ''),
                    'end': current_entry.get('end', ''),
                    'text_en': current_entry.get('text_en', ''),
                    'text_ko': current_entry.get('text_ko', '')
                })
        
        i += 1
    
    return shorts_data

def display_shorts(shorts_data):
    """Display extracted shorts segments"""
    for short_num in sorted(shorts_data.keys()):
        print(f"\n# shorts {short_num}")
        print()
        
        for entry in shorts_data[short_num]:
            print(entry['text_ko'])
        
        print()

def save_shorts_to_files(shorts_data, output_dir):
    """Save shorts segments to files (both EN and KO)"""
    import os
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save individual files for each short
    for short_num in sorted(shorts_data.keys()):
        filename = os.path.join(output_dir, f'shorts_{short_num}.txt')
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# shorts {short_num}\n\n")
            
            for entry in shorts_data[short_num]:
                f.write(f"[{entry['start']} - {entry['end']}]\n")
                f.write(f"EN: {entry['text_en']}\n")
                f.write(f"KO: {entry['text_ko']}\n\n")
        
        print(f"Saved: {filename}")
    
    # Save combined file with all shorts
    combined_filename = os.path.join(output_dir, 'shorts_all.txt')
    with open(combined_filename, 'w', encoding='utf-8') as f:
        for short_num in sorted(shorts_data.keys()):
            f.write(f"\n{'='*80}\n")
            f.write(f"# shorts {short_num}\n")
            f.write(f"{'='*80}\n\n")
            
            for entry in shorts_data[short_num]:
                f.write(f"[{entry['start']} - {entry['end']}]\n")
                f.write(f"EN: {entry['text_en']}\n")
                f.write(f"KO: {entry['text_ko']}\n\n")
    
    print(f"Saved: {combined_filename}")
    
    # Save Korean-only files
    for short_num in sorted(shorts_data.keys()):
        filename = os.path.join(output_dir, f'shorts_{short_num}_ko.txt')
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# shorts {short_num}\n\n")
            
            for entry in shorts_data[short_num]:
                f.write(f"{entry['text_ko']}\n")
        
        print(f"Saved: {filename}")
    
    # Save English-only files
    for short_num in sorted(shorts_data.keys()):
        filename = os.path.join(output_dir, f'shorts_{short_num}_en.txt')
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# shorts {short_num}\n\n")
            
            for entry in shorts_data[short_num]:
                f.write(f"{entry['text_en']}\n")
        
        print(f"Saved: {filename}")

def main():
    import os
    
    filepath = r'c:\deepskill_local\adhoc-2026\0122_chris_interview\subtitle_final.yaml'
    output_dir = os.path.join(os.path.dirname(filepath), 'shorts_output')
    
    print("Extracting shorts segments...")
    shorts_data = parse_yaml_file(filepath)
    
    print(f"Found {len(shorts_data)} shorts with {sum(len(v) for v in shorts_data.values())} total entries\n")
    print("=" * 80)
    
    # Display to console
    display_shorts(shorts_data)
    
    # Save to files
    print("\n" + "=" * 80)
    print("Saving outputs to files...")
    print("=" * 80)
    save_shorts_to_files(shorts_data, output_dir)
    print(f"\nAll files saved to: {output_dir}")

if __name__ == '__main__':
    main()
