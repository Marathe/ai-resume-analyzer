#!/usr/bin/env python
"""Debug script to see what experience intervals are being detected from Resume.docx"""

import sys
from utils.parser import ResumeParser
from utils.skills import SkillsExtractor

# Parse the resume
try:
    txt = ResumeParser.parse_file('uploads/Resume.docx')
except Exception as e:
    print(f"Error parsing resume: {e}")
    sys.exit(1)

# Print the raw text (first 3000 chars) to see date formats
print("=" * 80)
print("RAW RESUME TEXT (first 3000 characters):")
print("=" * 80)
print(txt[:3000])
print("\n" + "=" * 80)

# Now extract years (this will print debug info to stderr)
print("\nExtracting years of experience...")
years = SkillsExtractor.extract_years_of_experience(txt)

print("\n" + "=" * 80)
print(f"RESULT: {years} years")
print("=" * 80)

