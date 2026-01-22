#!/usr/bin/env python3
"""
Script to merge Korean subtitles with English subtitles and output revised YAML.
"""

import csv
import yaml
import re
from typing import List, Dict, Tuple

def parse_timestamp(ts: str) -> float:
    """Convert timestamp HH:MM:SS:FF to seconds (assuming 25fps)."""
    parts = ts.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = int(parts[2])
    frames = int(parts[3])
    return hours * 3600 + minutes * 60 + seconds + frames / 25.0

def load_korean_csv(filepath: str) -> List[Dict]:
    """Load Korean subtitles from CSV."""
    entries = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entries.append({
                'start': row['Start Time'],
                'end': row['End Time'],
                'text': row['Text'],
                'start_sec': parse_timestamp(row['Start Time']),
                'end_sec': parse_timestamp(row['End Time'])
            })
    return entries

def load_english_yaml(filepath: str) -> List[Dict]:
    """Load English subtitles from YAML."""
    with open(filepath, 'r', encoding='utf-8') as f:
        entries = yaml.safe_load(f)
    for entry in entries:
        entry['start_sec'] = parse_timestamp(entry['start'])
        entry['end_sec'] = parse_timestamp(entry['end'])
    return entries

def find_matching_korean(en_entry: Dict, ko_entries: List[Dict]) -> str:
    """Find Korean subtitle(s) that match the English entry's time range."""
    en_start = en_entry['start_sec']
    en_end = en_entry['end_sec']
    en_mid = (en_start + en_end) / 2
    
    matching = []
    for ko in ko_entries:
        ko_start = ko['start_sec']
        ko_end = ko['end_sec']
        ko_mid = (ko_start + ko_end) / 2
        
        # Check if Korean segment's midpoint falls within English segment's range
        # This prevents the same Korean segment from being matched to multiple English segments
        if en_start <= ko_mid < en_end:
            matching.append({
                'text': ko['text'],
                'start': ko_start,
                'mid': ko_mid
            })
    
    # Sort by start time
    matching.sort(key=lambda x: x['start'])
    
    # Extract texts, removing exact duplicates
    seen = set()
    unique_texts = []
    for m in matching:
        text = m['text'].strip()
        if text and text not in seen:
            seen.add(text)
            unique_texts.append(text)
    
    return ' '.join(unique_texts)

def merge_subtitles(en_entries: List[Dict], ko_entries: List[Dict]) -> List[Dict]:
    """Merge English and Korean subtitles."""
    merged = []
    for en in en_entries:
        ko_text = find_matching_korean(en, ko_entries)
        merged.append({
            'start': en['start'],
            'end': en['end'],
            'text_en': en['text_en'],
            'text_ko': ko_text if ko_text else ''
        })
    return merged

def save_yaml(entries: List[Dict], filepath: str):
    """Save merged entries to YAML with proper formatting."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(f"- start: {entry['start']}\n")
            f.write(f"  end: {entry['end']}\n")
            
            # Handle text_en - use quotes if contains newlines or special chars
            text_en = entry['text_en']
            if '\n' in text_en or '"' in text_en:
                # Use literal block scalar for multiline
                text_en_escaped = text_en.replace('"', '\\"')
                f.write(f'  text_en: "{text_en_escaped}"\n')
            else:
                f.write(f'  text_en: "{text_en}"\n')
            
            # Handle text_ko
            text_ko = entry['text_ko']
            if text_ko:
                f.write(f'  text_ko: {text_ko}\n')
            else:
                f.write(f'  text_ko: ""\n')

def main():
    # Load files
    print("Loading English YAML...")
    en_entries = load_english_yaml('subtitle_reviewed.yaml')
    print(f"Loaded {len(en_entries)} English entries")
    
    print("Loading Korean CSV...")
    ko_entries = load_korean_csv('subtitle_ko.csv')
    print(f"Loaded {len(ko_entries)} Korean entries")
    
    # Merge
    print("Merging subtitles...")
    merged = merge_subtitles(en_entries, ko_entries)
    
    # Save intermediate result
    print("Saving merged result...")
    save_yaml(merged, 'subtitle_merged.yaml')
    print("Done! Output saved to subtitle_merged.yaml")

if __name__ == '__main__':
    main()
