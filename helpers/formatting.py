import re

def format_claims(text):
    # Remove leading 'claims' headers if present
    text = re.sub(r'^claims.*?:', '', text, flags=re.IGNORECASE).strip()

    # Insert two newlines before each claim number at the start or after a period
    formatted = re.sub(r'(?<=\\s)(\\d+\\.\\s)', r'\\n\\n\\1', text)
    formatted = re.sub(r'^(\\d+\\.\\s)', r'\\n\\n\\1', formatted)

    # Remove excess spaces for consistency
    formatted = re.sub(r'\\s+', ' ', formatted)

    # Ensure actual newlines (not escaped backslashes)
    formatted = formatted.replace(' \\n\\n', '\\n\\n').replace('\\n\\n', '\\n\\n')

    return formatted.strip()
