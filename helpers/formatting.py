import re

def format_claims(text):
    # Insert two real newlines before each claim number (e.g., "1. ")
    formatted = re.sub(r'(\\b\\d+\\.\\s+)', r'\\n\\n\\1', text)

    # Replace escaped \\n with real newlines (in case any remain)
    formatted = formatted.replace('\\\\n', '\\n')

    return formatted.strip()
