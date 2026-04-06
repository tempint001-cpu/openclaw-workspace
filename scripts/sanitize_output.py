#!/usr/bin/env python3
"""
Sanitize output to strip NO_REPLY and other artifacts.
Usage: python3 sanitize_output.py < input.txt > output.txt
"""
import sys
import re

def sanitize(text):
    if not text:
        return ""
    # Remove NO_REPLY variations
    text = re.sub(r'\s*[\[\(]?\s*NO_REPLY\s*[\]\)]?\s*', '', text, flags=re.IGNORECASE)
    # Remove trailing ] bracket artifacts
    text = re.sub(r'\]\s*$', '', text)
    # Strip
    text = text.strip()
    return text

if __name__ == "__main__":
    output = sys.stdin.read()
    print(sanitize(output), end='')