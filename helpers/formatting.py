import re

def format_claims(text):
    # Use regex to find claim numbers and split before them
    claims = re.split(r'(\\d+\\.\\s+)', text)
    
    # Rebuild with double newlines before claim numbers
    formatted_claims = ""
    i = 0
    while i < len(claims):
        if re.match(r'\\d+\\.\\s+', claims[i]):
            formatted_claims += "\\n\\n" + claims[i] + claims[i + 1].strip()
            i += 2
        else:
            formatted_claims += claims[i].strip()
            i += 1

    # Replace multiple spaces with a single space for cleanliness
    formatted_claims = re.sub(r'\\s{2,}', ' ', formatted_claims)

    # Ensure that single newlines render correctly
    return formatted_claims
