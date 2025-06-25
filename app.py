import streamlit as st
import pandas as pd
import requests
import zipfile
import io
from bs4 import BeautifulSoup
import time

# ----------------------------
# Constants and headers
# ----------------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}
FDA_BASE_URL = "https://www.fda.gov/drugs/novel-drug-approvals-fda/novel-drug-approvals-"
ORANGE_BOOK_URL = "https://www.fda.gov/media/76860/download?attachment"

# ----------------------------
# Helper Functions
# ----------------------------

def normalize(text):
    return str(text).lower().replace(" ", "").replace("-", "").strip()

def scrape_fda_novel_approvals(year):
    url = f"{FDA_BASE_URL}{year}"
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table")
    df = pd.read_html(str(table))[0]
    df.columns = [col.strip() for col in df.columns]
    df["normalized_name"] = df["Drug Name"].apply(normalize)
    return df

def load_orange_book():
    response = requests.get(ORANGE_BOOK_URL, headers=HEADERS)
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall("orange_book_data")
    products = pd.read_csv("orange_book_data/products.txt", sep="~", dtype=str)
    patents = pd.read_csv("orange_book_data/patent.txt", sep="~", dtype=str)
    patents["Drug_Substance_Flag"] = patents["Drug_Substance_Flag"].str.upper() == "Y"
    patents["Drug_Product_Flag"] = patents["Drug_Product_Flag"].str.upper() == "Y"
    return products, patents

def parse_patent_google(patent_number):
    url = f"https://patents.google.com/patent/US{patent_number}/en"
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    assignee_tag = soup.find("dd", itemprop="assigneeOriginal")
    assignee = assignee_tag.text.strip() if assignee_tag else "Unknown"
    claims_block = soup.find("section", itemprop="claims")
    claims = claims_block.get_text(separator=' ', strip=True).lower() if claims_block else ""

    def found(text, keywords):
        return any(kw in text for kw in keywords)

    keywords = {
        "crystalline": ["crystalline"],
        "amorphous": ["amorphous", "solid dispersion", "disordered"],
        "salt": ["salt"],
        "solid_dispersion": ["solid dispersion", "amorphous dispersion", "molecular dispersion", "polymeric carrier"],
        "biologic": ["monoclonal antibody", "biosimilar", "recombinant", "protein", "gene therapy", "biologic"]
    }

    return {
        "Crystalline": found(claims, keywords["crystalline"]),
        "SF": found(claims, keywords["crystalline"]),
        "Amorphous": found(claims, keywords["amorphous"]),
        "Salt": found(claims, keywords["salt"]),
        "Solid-Dispersion": found(claims, keywords["solid_dispersion"]),
        "Biologic": found(claims, keywords["biologic"]),
        "Assignee": assignee,
        "Claims": claims
    }

# ----------------------------
# Streamlit UI
# ----------------------------

st.title("FDA Drug Patent Analysis UI")
year = st.text_input("Enter Year for FDA Novel Drug Approvals", "2025")

if st.button("Run Analysis"):
    with st.spinner("Scraping FDA and Orange Book data..."):
        fda_df = scrape_fda_novel_approvals(year)
        products_df, patents_df = load_orange_book()
        products_df["normalized_trade_name"] = products_df["Trade_Name"].apply(normalize)
        matched_products = products_df[products_df["normalized_trade_name"].isin(fda_df["normalized_name"])]

        patents_df["Appl_No"] = patents_df["Appl_No"].astype(str)
        patents_df["Product_No"] = patents_df["Product_No"].astype(str)
        matched_products["Appl_No"] = matched_products["Appl_No"].astype(str)
        matched_products["Product_No"] = matched_products["Product_No"].astype(str)

        merged_df = pd.merge(matched_products, patents_df, on=["Appl_No", "Product_No"], how="left")
        merged_df.dropna(subset=["Patent_No"], inplace=True)

        # Initialize fields
        for col in ["Crystalline", "SF", "Amorphous", "Salt", "Solid-Dispersion", "Biologic"]:
            merged_df[col] = False
        merged_df["Assignee"] = "Unknown"
        merged_df["Claims"] = ""

        patent_cache = {}
        for patent in merged_df["Patent_No"].dropna().unique():
            try:
                parsed = parse_patent_google(patent)
                for key, val in parsed.items():
                    merged_df.loc[merged_df["Patent_No"] == patent, key] = val
                time.sleep(1)
            except:
                continue

        # Rename
        merged_df.rename(columns={
            "normalized_trade_name": "Drug Name",
            "Ingredient": "Active Ingredient",
            "Patent_No": "Patent Number",
            "Patent_Expire_Date_Text": "Expiration Date",
            "Approval_Date": "Approval Date",
            "Drug_Substance_Flag": "DS",
            "Drug_Product_Flag": "DP",
            "Applicant_Full_Name": "NDA Holder"
        }, inplace=True)

        desired_order = [
            "Drug Name", "Active Ingredient", "Approval Date", "Patent Number", "Expiration Date",
            "DS", "DP", "SF", "Crystalline", "Salt", "Amorphous", "Solid-Dispersion", "Biologic",
            "NDA Holder", "Assignee"
        ]

        for col in desired_order:
            if col not in merged_df:
                merged_df[col] = False

        merged_df = merged_df[desired_order + [c for c in merged_df.columns if c not in desired_order]]
        st.success(f"✅ {len(merged_df)} matched entries found.")

        selected_row = st.selectbox("Select a drug to view claims:", merged_df["Drug Name"].unique())
        selected_claims = merged_df[merged_df["Drug Name"] == selected_row]["Claims"].iloc[0]
        st.text_area("Patent Claims:", selected_claims, height=300)

        editable_cols = ["DS", "DP", "SF", "Crystalline", "Salt"]
        st.markdown("### Update Flags:")
        for col in editable_cols:
            merged_df.loc[merged_df["Drug Name"] == selected_row, col] = st.checkbox(col, value=merged_df.loc[merged_df["Drug Name"] == selected_row, col].iloc[0])

        st.dataframe(merged_df[merged_df["Drug Name"] == selected_row])
        st.download_button("Download CSV", merged_df.to_csv(index=False), file_name="drug_patents.csv")