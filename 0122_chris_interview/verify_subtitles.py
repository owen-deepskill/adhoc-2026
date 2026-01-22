#!/usr/bin/env python3
"""Verify the processed subtitles for quality"""

import yaml

def verify_subtitles(yaml_path: str):
    with open(yaml_path, 'r', encoding='utf-8') as f:
        subs = yaml.safe_load(f)
    
    print(f"Total entries: {len(subs)}")
    
    # Count entries with both text_en and text_ko
    complete = sum(1 for s in subs if s.get('text_en') and s.get('text_ko'))
    print(f"Entries with both EN and KO: {complete}")
    
    # Check chunk lengths
    en_too_long = []
    ko_too_long = []
    
    for i, s in enumerate(subs):
        en = s.get('text_en', '')
        ko = s.get('text_ko', '')
        
        if len(en) > 90:
            en_too_long.append((i, len(en), en[:50]))
        if len(ko) > 80:  # Korean typically longer due to overlapping matches
            ko_too_long.append((i, len(ko)))
    
    print(f"\nEN entries > 90 chars: {len(en_too_long)}")
    if en_too_long[:5]:
        print("  First 5 examples:")
        for idx, length, preview in en_too_long[:5]:
            print(f"    Entry {idx}: {length} chars - '{preview}...'")
    
    print(f"\nKO entries > 80 chars: {len(ko_too_long)}")
    
    # Check for remaining issues
    issues = []
    for i, s in enumerate(subs):
        en = s.get('text_en', '')
        # Check for remaining interjections at start
        if en.lower().startswith(('yeah,', 'right,', 'okay,', 'exactly,')):
            issues.append((i, 'interjection', en[:30]))
        # Check for weird patterns
        if en.startswith(("'?", "? ")):
            issues.append((i, 'weird_start', en[:30]))
    
    print(f"\nRemaining issues found: {len(issues)}")
    for idx, issue_type, preview in issues[:10]:
        print(f"  Entry {idx}: {issue_type} - '{preview}'")
    
    print("\nVerification complete!")

if __name__ == '__main__':
    verify_subtitles('subtitle_final.yaml')
