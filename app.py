import streamlit as st
import pandas as pd
from helpers.generate_merged_df import generate_merged_df
from helpers.formatting import format_claims

st.set_page_config(page_title="Drug Patent Claim Analyzer", layout="wide", initial_sidebar_state="expanded")

st.sidebar.image("firm_logo.png", use_container_width=True)
st.sidebar.markdown("---")
st.sidebar.header("🔍 Search Novel Drug Approvals by Year")
year = st.sidebar.number_input("FDA Approval Year", min_value=2000, max_value=2100, value=2025)

if st.sidebar.button("Fetch and Analyze Patents"):
    with st.spinner("Fetching data from FDA Novel Drug Approvals, Orange Book, and Google Patents. This may take a few minutes..."):
        df = generate_merged_df(year)
        st.session_state["patent_df"] = df
        st.success("✅ Data loaded successfully!")

st.sidebar.markdown("### Filter Results By:")
show_crystalline = st.sidebar.checkbox("Show Crystalline", value=False)
show_salt = st.sidebar.checkbox("Show Salt", value=False)
show_amorphous = st.sidebar.checkbox("Show Amorphous", value=False)

st.title("🔬 The Orange Bookinator")
st.caption("Automated extraction and analysis of solid-form, salt, and amorphous patent claims.")

if "patent_df" in st.session_state:
    df = st.session_state["patent_df"]
    filtered_df = df.copy()
    if show_crystalline:
        filtered_df = filtered_df[filtered_df["Crystalline"] == True]
    if show_salt:
        filtered_df = filtered_df[filtered_df["Salt"] == True]
    if show_amorphous:
        filtered_df = filtered_df[filtered_df["Amorphous"] == True]

    st.subheader("Drug and Patent Data")
    st.caption("To edit drug form, check or uncheck the cell")
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

    buffer = pd.ExcelWriter("Patent_Data.xlsx", engine="xlsxwriter")
    edited_df.to_excel(buffer, index=False, sheet_name="Patent Data")
    buffer.close()
    with open("Patent_Data.xlsx", "rb") as file:
        st.download_button(
            label="📥 Download Table as Excel",
            data=file,
            file_name="Patent_Data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

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
    st.info("Use the sidebar to fetch and analyze patent data for the selected year.")

st.markdown("---")
st.caption("© 2025 Barash Law LLC | Confidential | Internal Use Only")
