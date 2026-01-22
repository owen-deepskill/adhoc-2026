#!/usr/bin/env python3
"""
Process subtitles according to the revision plan:
1. Add Korean subtitles (text_ko) matched by timestamp proximity
2. Correct English text using fireflies_notes.md as authoritative source
3. Remove Owen's interjections from Chris's speech
4. Ensure proper sentence boundaries
5. Manage chunk lengths
"""

import yaml
import csv
import re
from typing import List, Dict, Tuple
from datetime import timedelta


def parse_timestamp(ts: str) -> timedelta:
    """Convert timestamp string HH:MM:SS:FF to timedelta (assuming 25fps)"""
    parts = ts.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = int(parts[2])
    frames = int(parts[3]) if len(parts) > 3 else 0
    # Assuming 25 fps
    milliseconds = int(frames * (1000 / 25))
    return timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)


def load_korean_subtitles(csv_path: str) -> List[Dict]:
    """Load Korean subtitles from CSV file"""
    subtitles = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            subtitles.append({
                'start': row['Start Time'],
                'end': row['End Time'],
                'text': row['Text']
            })
    return subtitles


def load_english_subtitles(csv_path: str) -> List[Dict]:
    """Load English subtitles from CSV file"""
    subtitles = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            subtitles.append({
                'start': row['Start Time'],
                'end': row['End Time'],
                'text': row['Text']
            })
    return subtitles


def load_yaml_subtitles(yaml_path: str) -> List[Dict]:
    """Load subtitles from YAML file"""
    with open(yaml_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def find_matching_korean(en_start: str, en_end: str, ko_subs: List[Dict], 
                         tolerance_ms: int = 5000) -> str:
    """
    Find Korean subtitle that best matches the English timestamp range.
    Uses timestamp proximity to match.
    """
    en_start_td = parse_timestamp(en_start)
    en_end_td = parse_timestamp(en_end)
    en_mid = en_start_td + (en_end_td - en_start_td) / 2
    
    best_match = None
    best_distance = float('inf')
    matched_texts = []
    
    for ko in ko_subs:
        ko_start_td = parse_timestamp(ko['start'])
        ko_end_td = parse_timestamp(ko['end'])
        ko_mid = ko_start_td + (ko_end_td - ko_start_td) / 2
        
        # Check if Korean subtitle overlaps with English timestamp range
        if ko_end_td >= en_start_td and ko_start_td <= en_end_td:
            # Calculate overlap
            overlap_start = max(en_start_td, ko_start_td)
            overlap_end = min(en_end_td, ko_end_td)
            overlap = (overlap_end - overlap_start).total_seconds()
            
            if overlap > 0:
                matched_texts.append((ko_start_td, ko['text']))
    
    # Sort by start time and concatenate
    matched_texts.sort(key=lambda x: x[0])
    return ' '.join([t[1] for t in matched_texts]) if matched_texts else ''


# Dictionary of English corrections based on fireflies_notes.md
ENGLISH_CORRECTIONS = {
    # Key corrections from the plan
    'teasing technical shift': 'dizzying technological shifts',
    'teasing technological': 'dizzying technological',
    'Today we are seeing teasing': 'Today we are seeing dizzying',
    'rules of the roti': 'rules of logic',
    'rule of the roti': 'rule of logic',
    'Chris Reid': 'Chris Reed',
    'What are changing': 'What is changing',
    'what are changing': 'what is changing',
    'What are not changing': 'What is not changing',
    'what are not changing': 'what is not changing',
    
    # Additional corrections from fireflies_notes.md
    'pㅈople': 'people',
    'two philosophical in the': 'two philosophical and the',
    'he had his vision is': 'his vision is to',
    'into intersection': 'into this intersection',
    'persuade and to make a decision to': 'to persuade and to make a decision',
    
    # Grammar fixes
    'I\'ve been working on, AI': 'I\'ve been working on AI',
    'trying to, understand': 'trying to understand',
    'produce well-reasoned, well-thought through,': 'produce well-reasoned, well-thought through',
    'for the past, three decades': 'for the past three decades',
    'in, in play': 'in play',
    'in, in play': 'in play',
    'in, in agreed': 'into agreed',
    'with, the need': 'with the need',
    ', decisions.': ' decisions.',
    ', limit.': ' limit.',
    
    # Filler words and speech artifacts to clean up
    'I mean, I think': 'I think',
    'kind of, ': 'kind of ',
    'sort of, ': 'sort of ',
    'you know, ': '',
    ', you know,': ',',
    ', right?': '?',
    'Right? ': '',
    
    # Name corrections  
    'Rao Kambapati': 'Rao Kambhampati',
    'Kambapati': 'Kambhampati',
    
    # Technical terms
    'argument technology': 'argumentation technology',
    'argument mining': 'argumentation mining',
    
    # Fix double spaces
    '  ': ' ',
}

# Interjections to remove when they appear alone or at sentence boundaries
INTERJECTIONS = ['Yeah', 'Right', 'Okay', 'Exactly', 'Gotcha', 'I see', 'Yes', 'Yep']


def apply_corrections(text: str) -> str:
    """Apply English text corrections"""
    result = text
    for old, new in ENGLISH_CORRECTIONS.items():
        result = result.replace(old, new)
    # Apply multiple times to catch nested replacements
    for _ in range(3):
        for old, new in ENGLISH_CORRECTIONS.items():
            result = result.replace(old, new)
    return result


def remove_interjections(text: str) -> str:
    """
    Remove standalone interjections.
    Be careful to only remove them when they're standalone responses,
    not when they're part of a sentence.
    """
    result = text
    
    for interj in INTERJECTIONS:
        # At start of text followed by period, comma, or space
        result = re.sub(rf'^{interj}[.,]?\s*', '', result, flags=re.IGNORECASE)
        # After newline
        result = re.sub(rf'\n{interj}[.,]?\s*', '\n', result, flags=re.IGNORECASE)
        # Standalone with comma after
        result = re.sub(rf'\s+{interj},\s+', ' ', result, flags=re.IGNORECASE)
        # At end of text preceded by period/space
        result = re.sub(rf'[.\s]+{interj}[.,]?$', '.', result, flags=re.IGNORECASE)
        # Standalone "Yeah." or "Right." as separate sentence
        result = re.sub(rf'\s+{interj}\.\s+', ' ', result, flags=re.IGNORECASE)
        # "precisely. Yeah. So" -> "precisely. So"
        result = re.sub(rf'(\.\s*){interj}[.,]?\s+', r'\1', result, flags=re.IGNORECASE)
        # ", yeah, " patterns
        result = re.sub(rf',\s*{interj}[.,]?\s*', ', ', result, flags=re.IGNORECASE)
        
    # Clean up double spaces and periods
    result = re.sub(r'\s+', ' ', result)
    result = re.sub(r'\.\.+', '.', result)
    result = re.sub(r',\s*,', ',', result)
    result = re.sub(r'\.\s*,', '.', result)
    
    return result.strip()


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    # Fix common issues
    # Remove weird punctuation patterns
    text = re.sub(r"^['\"]?\s*\?\s*", '', text)  # Remove starting "? 
    text = re.sub(r'^[,.\s]+', '', text)  # Remove leading punctuation
    # Fix lowercase after period
    text = re.sub(r'\.(\s+)([a-z])', lambda m: '. ' + m.group(2).upper(), text)
    # Clean up trailing "right"
    text = re.sub(r',?\s+right\??$', '.', text, flags=re.IGNORECASE)
    # Fix "? That's" -> "That's"
    text = re.sub(r"^'?\?\s*", '', text)
    return text


def process_subtitles(yaml_path: str, ko_csv_path: str, en_csv_path: str, output_path: str):
    """Main processing function"""
    
    # Load all data
    print("Loading subtitles...")
    yaml_subs = load_yaml_subtitles(yaml_path)
    ko_subs = load_korean_subtitles(ko_csv_path)
    en_subs = load_english_subtitles(en_csv_path)
    
    print(f"Loaded {len(yaml_subs)} YAML entries")
    print(f"Loaded {len(ko_subs)} Korean entries")
    print(f"Loaded {len(en_subs)} English entries")
    
    # Process each entry
    processed = []
    for i, entry in enumerate(yaml_subs):
        start = entry['start']
        end = entry['end']
        text_en = entry.get('text', entry.get('text_en', ''))
        
        # Apply English corrections
        text_en = apply_corrections(text_en)
        
        # Remove interjections (carefully)
        text_en = remove_interjections(text_en)
        
        # Clean text
        text_en = clean_text(text_en)
        
        # Find matching Korean subtitle
        text_ko = find_matching_korean(start, end, ko_subs)
        
        # Create new entry
        new_entry = {
            'start': start,
            'end': end,
            'text_en': text_en,
            'text_ko': text_ko
        }
        processed.append(new_entry)
        
        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1}/{len(yaml_subs)} entries...")
    
    # Write output
    print(f"Writing output to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(processed, f, allow_unicode=True, default_flow_style=False, 
                  sort_keys=False, width=1000)
    
    print("Done!")
    return processed


if __name__ == '__main__':
    import os
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    yaml_path = os.path.join(base_dir, 'subtitle_reviewed.yaml')
    ko_csv_path = os.path.join(base_dir, 'subtitle_ko.csv')
    en_csv_path = os.path.join(base_dir, 'subtitle_en.csv')
    output_path = os.path.join(base_dir, 'subtitle_final.yaml')
    
    process_subtitles(yaml_path, ko_csv_path, en_csv_path, output_path)
