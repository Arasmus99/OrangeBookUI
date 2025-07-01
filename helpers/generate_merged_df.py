import requests
from bs4 import BeautifulSoup
import pandas as pd
import zipfile
import io
import time
import unicodedata

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

def scrape_fda_novel_approvals(year):
    url = f"https://www.fda.gov/drugs/novel-drug-approvals-fda/novel-drug-approvals-{year}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table")
    df_list = pd.read_html(str(table))
    fda_df = df_list[0]
    fda_df.columns = [col.strip() for col in fda_df.columns]
    return fda_df

def normalize(text):
    return str(text).lower().replace(" ", "").replace("-", "").strip()

def download_orange_book():
    orange_book_url = "https://www.fda.gov/media/76860/download?attachment"
    response = requests.get(orange_book_url, headers=HEADERS)
    response.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall("orange_book_data")

def load_orange_book_data():
    products_df = pd.read_csv("orange_book_data/products.txt", sep="~", dtype=str)
    patents_df = pd.read_csv("orange_book_data/patent.txt", sep="~", dtype=str)

    patents_df["Drug_Substance_Flag"] = patents_df["Drug_Substance_Flag"].apply(lambda x: str(x).strip().upper() == "Y")
    patents_df["Drug_Product_Flag"] = patents_df["Drug_Product_Flag"].apply(lambda x: str(x).strip().upper() == "Y")
    return products_df, patents_df

def parse_patent_google(patent_number):
    url = f"https://patents.google.com/patent/US{patent_number}/en"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return None
    response.encoding = response.apparent_encoding  # let requests detect encoding
    decoded_content = response.content.decode(response.encoding, errors='replace')
    soup = BeautifulSoup(decoded_content, "html.parser")

    assignee_tag = soup.find("dd", itemprop="assigneeOriginal")
    assignee = assignee_tag.text.strip() if assignee_tag else "Unknown"

    # extract
    claims_block = soup.find("section", itemprop="claims")
    claims = claims_block.get_text(separator=' ', strip=True) if claims_block else ""
    
    # optional cleanup
    claims = claims.replace('\xa0', ' ').replace('\u2014', '-').replace('\u2013', '-')
    
    # normalize unicode
    claims = unicodedata.normalize("NFKC", claims)

    def found(text, keywords):
        return any(kw in text for kw in keywords)

    keywords = {
        "crystalline": ["crystalline"],
        "amorphous": ["amorphous", "solid dispersion", "disordered"],
        "salt": ["salt"],
    }

    return {
        "Crystalline": found(claims, keywords["crystalline"]),
        "SF": found(claims, keywords["crystalline"]),
        "Amorphous": found(claims, keywords["amorphous"]),
        "Salt": found(claims, keywords["salt"]),
        "Assignee": assignee,
        "Claims": claims
    }

def generate_merged_df(year):
    fda_df = scrape_fda_novel_approvals(year)
    download_orange_book()
    products_df, patents_df = load_orange_book_data()

    products_df["normalized_trade_name"] = products_df["Trade_Name"].apply(normalize)
    fda_df["normalized_name"] = fda_df["Drug Name"].apply(normalize)

    matched_products = products_df[products_df["normalized_trade_name"].isin(fda_df["normalized_name"])]

    for df in (patents_df, matched_products):
        df["Appl_No"] = df["Appl_No"].astype(str)
        df["Product_No"] = df["Product_No"].astype(str)

    merged_df = pd.merge(matched_products, patents_df, on=["Appl_No", "Product_No"], how="left")
    merged_df.dropna(subset=["Patent_No"], inplace=True)

    # Pre-fill
    merged_df["Crystalline"] = False
    merged_df["SF"] = False
    merged_df["Amorphous"] = False
    merged_df["Salt"] = False
    merged_df["Assignee"] = "Unknown"
    merged_df["Claims"] = ""

    parsed_cache = {}
    for i, patent in enumerate(merged_df["Patent_No"].dropna().unique()):
        print(f"🔎 [{i+1}] Patent US{patent}")
        if patent not in parsed_cache:
            result = parse_patent_google(patent)
            parsed_cache[patent] = result
            time.sleep(1)
        else:
            result = parsed_cache[patent]

        if result:
            for field in ["Crystalline", "SF", "Amorphous", "Salt", "Assignee", "Claims"]:
                merged_df.loc[merged_df["Patent_No"] == patent, field] = result[field]
    columns_to_drop = [
    "index", "DF;Route", "Trade_Name", "Applicant", "Strength",
    "Appl_Type_x", "Appl_No", "Product_No", "TE_Code",
    "RLD", "RS", "Type", "Appl_Type_y", "Patent_Use_Code", "Delist_Flag", "Submission_Date"
    ]

    # Drop only if they exist
    merged_df.drop(columns=[col for col in columns_to_drop if col in merged_df.columns], inplace=True)
    merged_df.rename(columns={
        "Patent_Expire_Date_Text": "Expiration Date",
        "Drug_Substance_Flag": "DS",
        "Drug_Product_Flag": "DP",
        "Applicant_Full_Name": "NDA Holder",
        "Patent_No": "Patent Number",
        "Ingredient": "Active Ingredient",
        "normalized_trade_name": "Drug Name"
    }, inplace=True)

    desired_order = [
        "Drug Name", "Active Ingredient", "Approval_Date", "Patent Number",
        "Expiration Date", "DS", "DP", "SF", "Crystalline", "Amorphous",
        "Salt", "NDA Holder", "Assignee", "Claims"
    ]

    for col in desired_order:
        if col not in merged_df.columns:
            merged_df[col] = None

    merged_df = merged_df.reindex(columns=desired_order + [c for c in merged_df.columns if c not in desired_order])
    return merged_df
