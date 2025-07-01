import re

def format_claims(text):
    # Insert double line breaks before each claim number
    formatted = re.sub(r'(\\b\\d+\\.\\s+)', r'\\n\\n\\1', text)  # may not render properly

    # Instead, insert actual newlines:
    formatted = re.sub(r'(\\b\\d+\\.\\s+)', r'\\n\\n\\1', text)

    # If still not breaking, force newlines using '\n' directly:
    formatted = re.sub(r'(\\b\\d+\\.\\s+)', r'\\n\\n\\1', text)

    # Optional: capitalize sentences
    sentences = re.split(r'(\\.|\\?|!)\\s+', formatted)
    sentences = [s.capitalize() for s in sentences]
    formatted = ' '.join(sentences)

    # Replace escaped newlines with real newlines
    formatted = formatted.replace('\\\\n', '\\n')

    return formatted.strip()
