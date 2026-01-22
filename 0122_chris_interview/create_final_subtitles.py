#!/usr/bin/env python3
"""
Comprehensive subtitle processor that creates high-quality subtitles with:
1. Proper sentence boundaries
2. Matched Korean translations
3. Corrected English text from Fireflies notes
4. Removed interjections
5. Appropriate chunk lengths
"""

import csv
import yaml
import re
import os
from typing import List, Dict, Tuple

# ============== CONFIGURATION ==============
MAX_EN_CHARS = 100  # Max characters per English subtitle chunk
MAX_KO_CHARS = 50   # Max characters per Korean subtitle chunk

# ============== ENGLISH CORRECTIONS ==============
ENGLISH_CORRECTIONS = [
    # Order matters - more specific first
    ("teasing technical shift", "dizzying technological shifts"),
    ("rules of the roti", "rules of logic"),
    ("rules of the logic", "rules of logic"),
    ("rule of the logic", "rules of logic"),
    ("Chris Reid", "Chris Reed"),
    ("What are changing", "What is changing"),
    ("what are not changing", "what is not changing"),
    ("pㅈople", "people"),
    ("There's not a lot of rule.", "There's not a lot of raw material."),
    ("There's not a lot of rule", "There's not a lot of raw material"),
    ("rhythms\n", "algorithms\n"),
    (" rhythms ", " algorithms "),
    ("rhythms for", "algorithms for"),
    ("developing rhythms", "developing algorithms"),
    ("LLM is out of the box", "LLMs, at least out of the box,"),
    ("So LLMs out of the box.", "So LLMs, at least out of the box,"),
    ("I thoroughly recommend the romance", "I thoroughly recommend the Moral Maze"),
    ("the romance.", "the Moral Maze."),
    ("I say formally, yeah. And more latterly,", "in the form of LLMs and more latterly,"),
    ("work that we'll be doing", "work that we've been doing"),
    ("presenting these things", "these things"),
    ("express confidence", "express conflict"),
    ("drive, are structured", "argumentation are structured"),
    ("boxes of arrows", "boxes and arrows"),
    ("best brass", "best grasp"),
    ("evidence drawn", "evidence driven"),
    ("a while.", "in the wild."),
    ("a while. So", "in the wild. So"),
    ("in the, the data", "in the data"),
    ("or dis confirm", "or disconfirm"),
    ("dis confirm", "disconfirm"),
    # Grammar fixes based on Fireflies
    ("logic persuade", "logic to persuade"),
    ("with they express", "when they express"),
    ("to to join", "to join"),
    ("here to to", "here to"),
    ("to to", "to"),
    ("he had his vision is kind of", "his vision is to"),
    ("So he had his vision is to", "So his vision is to"),
    ("philosophical in the technological", "philosophical and technological"),
    ("for last, last", "for the last"),
    ("for last,\nlast", "for the last"),
    (", last 2000", " 2000"),
    ("last, last", "the last"),
    ("  ", " "),
]

# Interjections to remove (Owen's reactions)
INTERJECTIONS_STANDALONE = [
    "Yeah, precisely.", "Yeah, yeah.", "Right, right.", "Gotcha, gotcha.",
    "Exactly, exactly.", "I see, yeah.", "Yeah.", "Right.", "Okay.", 
    "Exactly.", "Gotcha.", "I see.", "Right?", "Yeah?",
]

INTERJECTIONS_INLINE = [
    " Yeah, exactly. ", " Right. ", " Yeah. ", " Okay. ", " Exactly. ",
    "\nYeah. ", "\nRight. ", "\nOkay. ", "\nExactly. ",
    " Yeah.\n", " Right.\n", " Okay.\n", " Exactly.\n",
]

def parse_timestamp(ts: str) -> float:
    """Convert timestamp HH:MM:SS:FF to seconds (25fps)."""
    parts = ts.split(':')
    return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2]) + int(parts[3]) / 25.0

def seconds_to_timestamp(secs: float) -> str:
    """Convert seconds to timestamp string."""
    h = int(secs // 3600)
    m = int((secs % 3600) // 60)
    s = int(secs % 60)
    f = int((secs % 1) * 25)
    return f"{h:02d}:{m:02d}:{s:02d}:{f:02d}"

def load_csv(filepath: str) -> List[Dict]:
    """Load subtitles from CSV."""
    entries = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = row['Text'].strip()
            if text:
                entries.append({
                    'start': row['Start Time'],
                    'end': row['End Time'],
                    'text': text,
                    'start_sec': parse_timestamp(row['Start Time']),
                    'end_sec': parse_timestamp(row['End Time'])
                })
    return entries

def load_yaml(filepath: str) -> List[Dict]:
    """Load subtitles from YAML."""
    with open(filepath, 'r', encoding='utf-8') as f:
        entries = yaml.safe_load(f)
    for e in entries:
        e['start_sec'] = parse_timestamp(e['start'])
        e['end_sec'] = parse_timestamp(e['end'])
        if 'text' in e and 'text_en' not in e:
            e['text_en'] = e['text']
    return entries

def apply_corrections(text: str) -> str:
    """Apply all English corrections."""
    result = text
    for old, new in ENGLISH_CORRECTIONS:
        result = result.replace(old, new)
    return result

def remove_interjections(text: str) -> str:
    """Remove Owen's interjections."""
    result = text
    
    # Remove standalone interjections at start
    for intj in INTERJECTIONS_STANDALONE:
        if result.startswith(intj + " "):
            result = result[len(intj):].strip()
        elif result.startswith(intj + "\n"):
            result = result[len(intj):].strip()
    
    # Remove standalone interjections at end
    for intj in INTERJECTIONS_STANDALONE:
        if result.endswith(" " + intj):
            result = result[:-len(intj)-1].strip()
        elif result.endswith("\n" + intj):
            result = result[:-len(intj)-1].strip()
    
    # Remove inline interjections
    for intj in INTERJECTIONS_INLINE:
        result = result.replace(intj, " ")
    
    # Clean up multiple spaces
    result = re.sub(r' +', ' ', result)
    result = re.sub(r'\n +', '\n', result)
    result = re.sub(r' +\n', '\n', result)
    
    return result.strip()

def find_korean_for_timerange(start_sec: float, end_sec: float, ko_entries: List[Dict]) -> str:
    """Find Korean text that falls within the given time range."""
    texts = []
    for ko in ko_entries:
        ko_mid = (ko['start_sec'] + ko['end_sec']) / 2
        # Check if Korean midpoint falls within English range
        if start_sec <= ko_mid < end_sec:
            texts.append(ko['text'])
        # Also check significant overlap
        elif ko['start_sec'] < end_sec and ko['end_sec'] > start_sec:
            overlap_start = max(start_sec, ko['start_sec'])
            overlap_end = min(end_sec, ko['end_sec'])
            overlap = overlap_end - overlap_start
            ko_duration = ko['end_sec'] - ko['start_sec']
            if ko_duration > 0 and overlap / ko_duration > 0.5:
                if ko['text'] not in texts:
                    texts.append(ko['text'])
    
    return ' '.join(texts)

def merge_entries_by_sentence(en_entries: List[Dict], ko_entries: List[Dict]) -> List[Dict]:
    """Merge entries to have complete sentences, while respecting length limits."""
    result = []
    i = 0
    
    while i < len(en_entries):
        current = en_entries[i].copy()
        text_en = current.get('text_en', current.get('text', ''))
        text_en = apply_corrections(text_en)
        text_en = remove_interjections(text_en)
        
        if not text_en.strip():
            i += 1
            continue
        
        start_sec = current['start_sec']
        end_sec = current['end_sec']
        
        # Try to complete sentences by looking ahead (but respect length limits)
        while i + 1 < len(en_entries):
            next_entry = en_entries[i + 1]
            next_text = next_entry.get('text_en', next_entry.get('text', ''))
            next_text = apply_corrections(next_text)
            next_text = remove_interjections(next_text)
            
            if not next_text.strip():
                i += 1
                continue
            
            # Check if current text ends mid-sentence
            text_stripped = text_en.strip()
            ends_with_terminal = text_stripped.endswith(('.', '?', '!', '"'))
            
            # Check if current is very short (less than 40 chars) - try to merge
            is_very_short = len(text_stripped) < 40
            # Also check if next entry would have no Korean text alone
            next_start_sec = next_entry['start_sec']
            next_end_sec = next_entry['end_sec']
            next_ko = find_korean_for_timerange(next_start_sec, next_end_sec, ko_entries)
            ko_would_be_empty = not next_ko.strip()
            
            # Check length constraint
            combined_length = len(text_en) + len(next_text) + 1
            
            # Merge if:
            # 1. Current doesn't end with terminal punctuation OR is very short
            # 2. Combined length is reasonable
            # 3. Time gap is small
            time_gap = next_entry['start_sec'] - end_sec
            
            should_merge = (
                (not ends_with_terminal or is_very_short or ko_would_be_empty) and 
                combined_length <= MAX_EN_CHARS * 1.5 and 
                time_gap < 1.0
            )
            
            if should_merge:
                text_en = text_en.strip() + ' ' + next_text.strip()
                end_sec = next_entry['end_sec']
                i += 1
            else:
                break
        
        # Clean the text
        text_en = re.sub(r' +', ' ', text_en).strip()
        text_en = text_en.replace(' \n', '\n').replace('\n ', '\n')
        
        # Get Korean text for this time range
        text_ko = find_korean_for_timerange(start_sec, end_sec, ko_entries)
        
        # Apply Korean corrections
        text_ko = text_ko.replace("추론 리듬", "추론 알고리즘")
        
        if text_en:
            result.append({
                'start': current['start'],
                'end': seconds_to_timestamp(end_sec),
                'start_sec': start_sec,
                'end_sec': end_sec,
                'text_en': text_en,
                'text_ko': text_ko
            })
        
        i += 1
    
    return result

def split_long_entries(entries: List[Dict], ko_entries: List[Dict]) -> List[Dict]:
    """Split entries that are too long."""
    result = []
    
    for entry in entries:
        text_en = entry['text_en']
        text_ko = entry['text_ko']
        
        # Check if needs splitting
        if len(text_en) <= MAX_EN_CHARS:
            result.append(entry)
            continue
        
        # Try to split at sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text_en)
        
        if len(sentences) > 1:
            # Calculate time per character
            duration = entry['end_sec'] - entry['start_sec']
            total_chars = len(text_en)
            
            current_start = entry['start_sec']
            current_text = ""
            
            for sent in sentences:
                if current_text and len(current_text) + len(sent) + 1 > MAX_EN_CHARS:
                    # Save current and start new
                    sent_duration = duration * (len(current_text) / total_chars)
                    current_end = current_start + sent_duration
                    
                    ko_for_chunk = find_korean_for_timerange(current_start, current_end, ko_entries)
                    
                    result.append({
                        'start': seconds_to_timestamp(current_start),
                        'end': seconds_to_timestamp(current_end),
                        'start_sec': current_start,
                        'end_sec': current_end,
                        'text_en': current_text.strip(),
                        'text_ko': ko_for_chunk
                    })
                    
                    current_start = current_end
                    current_text = sent
                else:
                    if current_text:
                        current_text += " " + sent
                    else:
                        current_text = sent
            
            # Add remaining text
            if current_text.strip():
                ko_for_chunk = find_korean_for_timerange(current_start, entry['end_sec'], ko_entries)
                result.append({
                    'start': seconds_to_timestamp(current_start),
                    'end': entry['end'],
                    'start_sec': current_start,
                    'end_sec': entry['end_sec'],
                    'text_en': current_text.strip(),
                    'text_ko': ko_for_chunk
                })
        else:
            # Can't split nicely, keep as is
            result.append(entry)
    
    return result

def fix_korean_sentence_boundaries(entries: List[Dict]) -> List[Dict]:
    """Fix Korean text to not break mid-sentence."""
    # This would require more sophisticated Korean NLP
    # For now, just clean up obvious issues
    for entry in entries:
        text_ko = entry.get('text_ko', '')
        if text_ko:
            # Remove trailing particles that should be at start of next
            text_ko = text_ko.strip()
            entry['text_ko'] = text_ko
    
    return entries

def merge_orphan_entries(entries: List[Dict]) -> List[Dict]:
    """Merge very short entries that have no Korean text with previous/next entries."""
    if len(entries) < 2:
        return entries
    
    result = []
    i = 0
    
    while i < len(entries):
        current = entries[i].copy()
        
        # Check if this is an orphan entry (short EN, no KO)
        is_orphan = (
            len(current['text_en']) < 40 and 
            not current.get('text_ko', '').strip()
        )
        
        if is_orphan and result:
            # Try to merge with previous entry
            prev = result[-1]
            prev_en = prev['text_en']
            combined = prev_en + ' ' + current['text_en']
            
            if len(combined) <= MAX_EN_CHARS * 1.5:
                # Merge with previous
                prev['text_en'] = combined.strip()
                prev['end'] = current['end']
                prev['end_sec'] = current['end_sec']
                i += 1
                continue
        
        if is_orphan and i + 1 < len(entries):
            # Try to merge with next entry
            next_entry = entries[i + 1]
            combined = current['text_en'] + ' ' + next_entry['text_en']
            
            if len(combined) <= MAX_EN_CHARS * 1.5:
                # Merge with next - update next entry and skip current
                entries[i + 1]['text_en'] = combined.strip()
                entries[i + 1]['start'] = current['start']
                entries[i + 1]['start_sec'] = current['start_sec']
                i += 1
                continue
        
        result.append(current)
        i += 1
    
    return result

def save_yaml(entries: List[Dict], filepath: str):
    """Save to YAML with proper formatting."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(f"- start: {entry['start']}\n")
            f.write(f"  end: {entry['end']}\n")
            
            # Format text_en
            text_en = entry['text_en']
            if '\n' in text_en or '"' in text_en:
                escaped = text_en.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
                f.write(f'  text_en: "{escaped}"\n')
            else:
                f.write(f'  text_en: "{text_en}"\n')
            
            # Format text_ko
            text_ko = entry.get('text_ko', '')
            if text_ko:
                f.write(f'  text_ko: {text_ko}\n')
            else:
                f.write(f'  text_ko: ""\n')

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("Loading English subtitles from YAML...")
    en_entries = load_yaml('subtitle_reviewed.yaml')
    print(f"  Loaded {len(en_entries)} entries")
    
    print("Loading Korean subtitles from CSV...")
    ko_entries = load_csv('subtitle_ko.csv')
    print(f"  Loaded {len(ko_entries)} entries")
    
    print("Processing and merging entries...")
    merged = merge_entries_by_sentence(en_entries, ko_entries)
    print(f"  After merge: {len(merged)} entries")
    
    print("Splitting long entries...")
    split = split_long_entries(merged, ko_entries)
    print(f"  After split: {len(split)} entries")
    
    print("Fixing Korean sentence boundaries...")
    fixed = fix_korean_sentence_boundaries(split)
    
    print("Merging orphan entries...")
    merged_orphans = merge_orphan_entries(fixed)
    print(f"  After orphan merge: {len(merged_orphans)} entries")
    
    print("Saving to subtitle_final.yaml...")
    save_yaml(merged_orphans, 'subtitle_final.yaml')
    
    # Stats
    with_ko = sum(1 for e in merged_orphans if e.get('text_ko'))
    avg_en_len = sum(len(e['text_en']) for e in merged_orphans) / len(merged_orphans) if merged_orphans else 0
    
    print(f"\n=== Statistics ===")
    print(f"Total entries: {len(merged_orphans)}")
    print(f"With Korean: {with_ko} ({100*with_ko/len(merged_orphans):.1f}%)" if merged_orphans else "No entries")
    print(f"Average EN length: {avg_en_len:.1f} chars")
    print("Done!")

if __name__ == '__main__':
    main()
