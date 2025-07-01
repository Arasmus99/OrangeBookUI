import re

def format_claims(text):
    # Remove leading 'claims' and similar headers if present
    text = re.sub(r'^claims.*?:', '', text, flags=re.IGNORECASE).strip()

    # Insert two newlines before each numbered claim for clear separation
    formatted = re.sub(r'(\\s)(\\d+\\.\\s)', r'\\n\\n\\2', text)

    # Optional: clean excessive spaces
    formatted = re.sub(r'\\s+', ' ', formatted)

    # Ensure that newlines render properly
    return formatted.strip()
