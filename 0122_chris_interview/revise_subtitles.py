#!/usr/bin/env python3
"""
Comprehensive script to revise subtitles:
1. Correct English text based on Fireflies transcript
2. Remove Owen's filler words
3. Clean up and consolidate text
4. Output final high-quality YAML
"""

import yaml
import re
from typing import List, Dict, Tuple

# Known corrections based on Fireflies transcript
ENGLISH_CORRECTIONS = {
    # Typos and errors
    "teasing technical shift": "dizzying technological shifts",
    "teasing technological shift": "dizzying technological shifts",
    "dizzying dizzying": "dizzying",
    "pㅈople": "people",
    "rules of the roti": "rules of logic", 
    "rules of the logic to persuade": "rules of logic to persuade",
    "rules of the logic": "rules of logic",
    "rule of the logic": "rule of logic",
    "philosophical in the technological": "philosophical and technological",
    "he had his vision is kind of provoke": "his vision is to provoke",
    "Chris Reid": "Chris Reed",
    "So he had his vision is kind of provoke": "His vision is to provoke",
    "researching into this, into intersection": "researching into this intersection",
    "So he had his vision": "So his vision",
    "linguistic material ultimately": "linguistic material",
    
    # More corrections from Fireflies
    "And I found that there is exactly": "And I found that there's exactly",
    "train of thought": "chain of thought",
    "we're at a very interesting": "we had a very interesting",
    "So argument technology is, is now at this": "So argument technology is now at this",
    "I say formally, yeah. And more latterly": "in the form of LLMs and more latterly",
    "large reasoning models": "large reasoning models, LRMs",
    "rhythms": "algorithms",
    "So we also started developing rhythms": "So we also started developing algorithms",
    "in, in as much as": "in as much as",
    "In, in as much as": "In as much as",
    "compatible": "Kambhampati",
    "rail company party": "Rao Kambhampati",
    "By rail company party": "By Rao Kambhampati",
    "rather had done": "Rao had done",
    "Raoul's": "Rao's",
    "Raoul": "Rao",
    "56 four": "GPT-4",
    "GPT four": "GPT-4",
    "54 would say": "GPT-4 would say",
    "54": "GPT-4",
    "gofi": "GOFAI",
    "go find good old fashioned AI": "GOFAI, good old fashioned AI",
    
    # Fix LLM/LRM references
    "So LLM is out of the box": "So LLMs, out of the box",
    "LLM out of the box": "LLMs, out of the box",
    "vanilla, like LLM": "vanilla LLM",
    "the state of the art is still not able  to cope": "the state of the art is still not able to cope",
    
    # Clean up duplicates
    "Right. Right,": "",
    "Yeah. Yeah,": "",
    "Right? Right.": "",
    "Yeah? Yeah.": "",
    ", yeah, yeah": "",
    "Yeah, yeah": "",
    ", , ": ", ",
    "  ": " ",
    
    # Fix grammar
    "there is just a lot": "there's just a lot",
    "we're seeing is that by": "we're seeing is that, by",
    "that's out there and the ability": "that's out there, and the ability",
    "in, in play": "in play",
    "into, into agreed": "into agreed",
    "That, that kind of comes together": "That kind of comes together",
    "to, to model": "to model",
    "to to join": "to join",
    "here to to join": "here to join",
    "rules of logic persuade": "rules of logic to persuade",
    "for last, last": "for the last",
    "so, so yeah, so first": "So, first",
    "So, so yeah, so first": "So, first",
    "rules of logic persuade": "rules of logic to persuade",
    "last, last 2000": "the last 2000",
    "with they express": "when they express",
    "the the kind of": "the kind of",
    "So, so you": "So you",
    "kind of, kind of": "kind of",
    "kind of comes together. So there's a lot": "comes together. So there's a lot",
    "able to, to deliver": "able to deliver",
    "able to, to model": "able to model",
    "to, to have": "to have",
    "to be able to, to tackle": "to be able to tackle",
    "to, to do": "to do",
    "these, these kind": "this kind",
    "this, this kind": "this kind",
    "this, this sort": "this sort",
    "working on, AI": "working on AI",
    "trying to, understand": "trying to understand",
    "people, produce": "people produce",
    "for, for": "for",
    "right, Right": "right",
    "yes, Yes": "yes",
    "exactly, Exactly": "exactly",
    "and, and": "and",
    "but, But": "but",
    "or, Or": "or",
    ", ,": ",",
}

# Filler words to remove when they appear alone or at sentence boundaries
FILLER_PATTERNS = [
    r'\s*\bYeah\.\s*',
    r'\s*\bRight\.\s*',
    r'\s*\bGotcha\.\s*',
    r'\s*\bExactly\.\s*',
    r'\s*\bOkay\.\s*',
    r'\s*\bYeah,\s+yeah\.\s*',
    r'\s*\bRight,\s+right\.\s*',
    r'^\s*Yeah\s*$',
    r'^\s*Right\s*$',
    r'^\s*Gotcha,\s*gotcha\.\s*$',
    r'^\s*I see,\s*yeah\.\s*$',
    r'\s*Yeah\.\s+Yeah\.\s*',
]

def load_yaml(filepath: str) -> List[Dict]:
    """Load YAML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def apply_corrections(text: str) -> str:
    """Apply known corrections to text."""
    result = text
    for wrong, correct in ENGLISH_CORRECTIONS.items():
        result = result.replace(wrong, correct)
    return result

def remove_fillers(text: str) -> str:
    """Remove standalone filler words."""
    result = text
    for pattern in FILLER_PATTERNS:
        result = re.sub(pattern, ' ', result, flags=re.IGNORECASE)
    
    # Clean up multiple spaces
    result = re.sub(r' +', ' ', result)
    result = re.sub(r'\n +', '\n', result)
    result = result.strip()
    
    return result

def clean_korean_text(text: str) -> str:
    """Clean up Korean text - remove duplicates and clean spacing."""
    if not text:
        return ""
    
    import re
    
    # Split into potential sentences by Korean sentence endings (다, 요, 죠, 니다, etc.)
    # Use a more comprehensive pattern
    sentences = re.split(r'(?<=[다요죠까])\s+(?=[가-힣])', text)
    
    # Also handle cases where sentences don't end properly
    # Try to find repeated phrases
    result_sentences = []
    
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        
        # Check if this sentence (or significant part) is already in results
        is_duplicate = False
        for existing in result_sentences:
            # Check for exact match or significant overlap
            if s == existing:
                is_duplicate = True
                break
            # Check if one is contained in the other (longer one wins)
            if len(s) > 10 and len(existing) > 10:
                if s in existing:
                    is_duplicate = True
                    break
                if existing in s:
                    # Replace with longer version
                    result_sentences.remove(existing)
                    break
        
        if not is_duplicate:
            result_sentences.append(s)
    
    result = ' '.join(result_sentences)
    
    # Additional cleanup: remove word-level duplicates that appear consecutively
    words = result.split()
    cleaned_words = []
    prev_word = None
    prev_prev_word = None
    
    i = 0
    while i < len(words):
        word = words[i]
        # Skip if this word equals the previous (simple duplicate)
        if word == prev_word:
            i += 1
            continue
        # Skip if this is part of a repeated phrase (2 words)
        if i >= 2 and prev_word and prev_prev_word:
            if i + 1 < len(words):
                # Check for "A B A B" pattern
                if words[i] == prev_prev_word and words[i+1] == prev_word:
                    i += 2
                    continue
        
        cleaned_words.append(word)
        prev_prev_word = prev_word
        prev_word = word
        i += 1
    
    result = ' '.join(cleaned_words)
    
    # Clean up multiple spaces
    result = re.sub(r' +', ' ', result)
    
    return result.strip()

def consolidate_entries(entries: List[Dict]) -> List[Dict]:
    """Consolidate fragmented entries where possible."""
    if not entries:
        return entries
    
    consolidated = []
    i = 0
    
    while i < len(entries):
        current = entries[i].copy()
        text_en = current.get('text_en', '')
        text_ko = current.get('text_ko', '')
        
        # Check if current entry ends mid-sentence and next starts continuing
        while i + 1 < len(entries):
            next_entry = entries[i + 1]
            next_text = next_entry.get('text_en', '')
            
            # Conditions to merge:
            # 1. Current ends without sentence-ending punctuation
            # 2. Next starts with lowercase
            # 3. Combined would be reasonable length
            current_text_stripped = text_en.rstrip()
            
            should_merge = False
            if current_text_stripped and not current_text_stripped[-1] in '.!?':
                if next_text and next_text[0].islower():
                    combined_len = len(text_en) + len(next_text)
                    if combined_len < 200:  # Keep subtitle readable
                        should_merge = True
            
            if should_merge:
                text_en = text_en.rstrip() + ' ' + next_text.lstrip()
                next_ko = next_entry.get('text_ko', '')
                if next_ko and text_ko:
                    text_ko = text_ko + ' ' + next_ko
                elif next_ko:
                    text_ko = next_ko
                current['end'] = next_entry['end']
                i += 1
            else:
                break
        
        current['text_en'] = text_en
        current['text_ko'] = text_ko
        consolidated.append(current)
        i += 1
    
    return consolidated

def format_text_for_yaml(text: str) -> str:
    """Format text for YAML output with proper escaping."""
    if not text:
        return '""'
    
    # Check if needs quoting
    needs_quotes = any(c in text for c in ['"', "'", ':', '#', '\n', '{', '}', '[', ']'])
    
    if '\n' in text:
        # Use quoted string with escaped newlines
        escaped = text.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'
    elif needs_quotes:
        escaped = text.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'
    else:
        return text

def save_final_yaml(entries: List[Dict], filepath: str):
    """Save entries to YAML with clean formatting."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(f"- start: {entry['start']}\n")
            f.write(f"  end: {entry['end']}\n")
            
            text_en = entry.get('text_en', '')
            text_ko = entry.get('text_ko', '')
            
            # Format text_en
            if '\n' in text_en:
                escaped = text_en.replace('"', '\\"')
                f.write(f'  text_en: "{escaped}"\n')
            elif '"' in text_en or ':' in text_en:
                escaped = text_en.replace('"', '\\"')
                f.write(f'  text_en: "{escaped}"\n')
            else:
                f.write(f'  text_en: "{text_en}"\n')
            
            # Format text_ko
            if text_ko:
                f.write(f'  text_ko: {text_ko}\n')
            else:
                f.write('  text_ko: ""\n')

def process_subtitles(input_file: str, output_file: str):
    """Main processing function."""
    print(f"Loading {input_file}...")
    entries = load_yaml(input_file)
    print(f"Loaded {len(entries)} entries")
    
    # Process each entry
    print("Applying corrections and cleaning...")
    for entry in entries:
        # Apply English corrections
        text_en = entry.get('text_en', '')
        text_en = apply_corrections(text_en)
        text_en = remove_fillers(text_en)
        entry['text_en'] = text_en.strip()
        
        # Clean Korean text
        text_ko = entry.get('text_ko', '')
        text_ko = clean_korean_text(text_ko)
        entry['text_ko'] = text_ko
    
    # Remove empty entries
    entries = [e for e in entries if e.get('text_en', '').strip()]
    
    # Consolidate fragmented entries
    print("Consolidating entries...")
    entries = consolidate_entries(entries)
    
    print(f"Final entry count: {len(entries)}")
    
    # Save result
    print(f"Saving to {output_file}...")
    save_final_yaml(entries, output_file)
    print("Done!")

if __name__ == '__main__':
    process_subtitles('subtitle_merged.yaml', 'subtitle_final.yaml')
