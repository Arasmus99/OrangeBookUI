import re
import pandas as pd
from pptx import Presentation
from datetime import date, timedelta
from dateutil.parser import parse
import streamlit as st
from io import BytesIO

# === Regex Patterns ===
PATTERNS = {
    "docket_number": re.compile(
        r"\b\d{4}-[A-Z]{2,}-\d{5}-\d{2}\b"           # e.g. 2018-LOW-68327-13
        r"|\b\d{5}-\d{2}\b"                           # e.g. 68327-13
        r"|\b\d{5}-\d{4}-\d{2}[A-Z]{2,4}\b"           # e.g. 01330-0004-00US
    ),
    "application_number": re.compile(r"\b\d{2}/\d{3}[,]?\d{3}\s+[A-Z]{2}\b"),
    "alt_application_number": re.compile(
        r"\b[Pp]\d{11}\s+[A-Z]{2}-\w{1,4}\b"
        r"|\b\d{5,12}(?:[.,]\d+)?\s+[A-Z]{2,3}\b"
    ),
    "pct_number": re.compile(r"PCT/[A-Z]{2}\d{4}/\d{6}"),
    "wipo_number": re.compile(r"\bWO\d{4}/\d{6}\b"),
    "date": re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b")
}

@@ -63,6 +64,7 @@
        "docket_number": None,
        "application_number": None,
        "pct_number": None,
        "wipo_number": None,
        "due_dates": [],
        "raw_text": "\n".join(lines)
    }
@@ -79,6 +81,9 @@
        elif not entry["application_number"] and PATTERNS["alt_application_number"].search(line):
            entry["application_number"] = PATTERNS["alt_application_number"].search(line).group(0)

        if not entry["wipo_number"] and PATTERNS["wipo_number"].search(line):
            entry["wipo_number"] = PATTERNS["wipo_number"].search(line).group(0)

        for match in PATTERNS["date"].findall(line):
            try:
                parsed = parse(match, dayfirst=False, fuzzy=True)
@@ -87,7 +92,7 @@
            except:
                continue

    if not (entry["docket_number"] or entry["application_number"] or entry["pct_number"]):
    if not (entry["docket_number"] or entry["application_number"] or entry["pct_number"] or entry["wipo_number"]):
        return []

    if entry["due_dates"]:
@@ -113,11 +118,12 @@
                        "Docket Number": entry["docket_number"],
                        "Application Number": entry["application_number"],
                        "PCT Number": entry["pct_number"],
                        "WIPO Number": entry["wipo_number"],
                        "Due Dates": "; ".join(entry["due_dates"])
                    })

    if not results:
        return pd.DataFrame(columns=["Slide", "Textbox Content", "Docket Number", "Application Number", "PCT Number", "Due Dates"])
        return pd.DataFrame(columns=["Slide", "Textbox Content", "Docket Number", "Application Number", "PCT Number", "WIPO Number", "Due Dates"])

    df = pd.DataFrame(results)
    df["Earliest Due Date"] = df["Due Dates"].apply(get_earliest_due_date)
