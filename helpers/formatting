import re

def format_claims(text):
    # Insert double line breaks before claim numbers
    formatted = re.sub(r'(\\b\\d+\\.\\s+)', r'\\n\\n\\1', text)
    # Optionally capitalize sentences:
    sentences = re.split(r'(\\.|\\?|!)\\s+', formatted)
    sentences = [s.capitalize() for s in sentences]
    formatted = ' '.join(sentences)
    return formatted.strip()
