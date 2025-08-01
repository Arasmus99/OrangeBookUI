import streamlit as st
import re
import pandas as pd
from helpers.generate_merged_df import generate_merged_df
from helpers.formatting import format_claims
from datetime import datetime

st.set_page_config(page_title="Novel Drug Search", layout="wide", initial_sidebar_state="expanded")

# === Firm Logo ===
st.sidebar.image("firm_logo.png", use_container_width=True)
st.sidebar.markdown("---")

# === Mode Selection ===
mode = st.sidebar.radio("Select Data Mode:", ["Single Year", "Range"], horizontal=True)

#Future years cannot be included
current_year = datetime.now().year

if mode == "Single Year":
    year = st.sidebar.number_input("Enter FDA Approval Year", min_value=2021, max_value=current_year, value=current_year)
else:
    year_range = st.sidebar.slider("Select FDA Approval Year Range", min_value=2021, max_value=current_year, value=(2021, current_year))

# === Fetch Button ===
if st.sidebar.button("Fetch and Analyze Patents"):
    with st.spinner("Fetching and analyzing data. This may take several minutes..."):
        try:
            if "patent_df" in st.session_state:
                del st.session_state["patent_df"]  # clear previous state

            if mode == "Single Year":
                st.sidebar.write(f"Scraping data for **{year}**...")
                df = generate_merged_df(year)
                df["Approval_Year"] = year
            else:
                dfs = []
                for yr in range(year_range[0], year_range[1] + 1):
                    st.sidebar.write(f"Scraping data for **{yr}**...")
                    df_year = generate_merged_df(yr)
                    df_year["Approval_Year"] = yr
                    dfs.append(df_year)
                df = pd.concat(dfs, ignore_index=True)

            st.session_state["patent_df"] = df
            st.success("✅ Data fetched and analyzed successfully.")
        except Exception as e:
            st.error(f"Data fetch failed: {e}")

# === Filters Header ===
st.sidebar.markdown("### Filter Results By")
show_crystalline = st.sidebar.checkbox("Show Crystalline", value=False)
show_salt = st.sidebar.checkbox("Show Salt", value=False)
show_amorphous = st.sidebar.checkbox("Show Amorphous", value=False)

# === Main Title ===
st.title("🔬 The Orange Bookinator")
st.caption("Automated extraction and analysis of novel drugs with therapeutic equivalence patent claims.")

if "patent_df" in st.session_state and st.session_state["patent_df"] is not None:
    df = st.session_state["patent_df"]
    filtered_df = df.copy()

    if show_crystalline:
        filtered_df = filtered_df[filtered_df["Crystalline"] == True]
    if show_salt:
        filtered_df = filtered_df[filtered_df["Salt"] == True]
    if show_amorphous:
        filtered_df = filtered_df[filtered_df["Amorphous"] == True]

    # === Editable Table ===
    st.subheader("📋 Editable Patent Data Table")
    edited_df = st.data_editor(
        filtered_df.drop(columns=["Claims"], errors='ignore'),
        num_rows="dynamic",
        use_container_width=True,
        key="editable_table"
    )

    if not edited_df.empty:
        for idx, row in edited_df.iterrows():
            patent_number = row["Patent Number"]
            if patent_number in df["Patent Number"].values:
                mask = df["Patent Number"] == patent_number
                for col in ["Crystalline", "Salt", "Amorphous"]:
                    if col in row and pd.notna(row[col]):
                        df.loc[mask, col] = row[col]
        st.session_state["patent_df"] = df

    # === Download Button ===
    if mode == "Single Year":
        filename = f"Patent_Data_{year}.xlsx"
    else:
        filename = f"Patent_Data_{year_range[0]}_{year_range[1]}.xlsx"

    with pd.ExcelWriter(filename, engine="xlsxwriter") as writer:
        edited_df.to_excel(writer, index=False, sheet_name="Patent Data")

    with open(filename, "rb") as file:
        st.download_button(
            label="📥 Download Table as Excel",
            data=file,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    # === View Claims ===
    st.subheader("📑 View Patent Claims")
    selected_patent = st.selectbox("Select Patent Number to View Claims:", edited_df["Patent Number"].dropna().unique())
    selected_row = df[df["Patent Number"] == selected_patent]
    if not selected_row.empty:
        raw_claims = selected_row["Claims"].values[0]
        formatted_claims = format_claims(raw_claims)
        st.markdown("#### Patent Claims")
        st.text_area(
            label="Claims (formatted for review and copy-paste):",
            value=formatted_claims,
            height=700,
            key="claims_text_area"
        )
else:
    st.info("Use the sidebar to fetch and analyze patent data for the selected year or year range.")

st.markdown("---")
st.caption("© 2025 Barash Law LLC | Internal Use Only")
