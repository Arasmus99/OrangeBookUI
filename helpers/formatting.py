def format_claims(text):
    # Remove initial 'claims (n)' header if present
    lowered = text.lower()
    if lowered.startswith("claims"):
        text = text[text.find(":") + 1:].strip() if ":" in text else text[text.find(")") + 1:].strip()

    # Split on occurrences like '1. ', '2. ', etc.
    parts = []
    temp = text.split()
    current_claim = []
    for word in temp:
        if word[:-1].isdigit() and word.endswith('.'):
            if current_claim:
                parts.append(' '.join(current_claim).strip())
            current_claim = [word]
        else:
            current_claim.append(word)
    if current_claim:
        parts.append(' '.join(current_claim).strip())

    # Join with double newlines for clean separation
    formatted = "\\n\\n".join(parts)

    return formatted
