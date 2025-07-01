import streamlit as st
import pandas as pd
from helpers.generate_merged_df import generate_merged_df
from helpers.formatting import format_claims

# ========== Streamlit Page Config ==========
st.set_page_config(
    page_title="Drug Patent Claim Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== Sidebar with Firm Branding ==========
st.sidebar.image("firm_logo.png", use_column_width=True)
st.sidebar.markdown("---")
st.sidebar.header("🔍 Filter Patents")
year = st.sidebar.number_input("FDA Approval Year", min_value=2000, max_value=2100, value=2025)

show_crystalline = st.sidebar.checkbox("Show Crystalline", value=False)
show_salt = st.sidebar.checkbox("Show Salt", value=False)
show_amorphous = st.sidebar.checkbox("Show Amorphous", value=False)

if st.sidebar.button("Fetch and Analyze Patents"):
    with st.spinner("Fetching FDA data, Orange Book data, and parsing Google Patents. This may take a few minutes..."):
        df = generate_merged_df(year)
        st.session_state["patent_df"] = df
        st.success("✅ Data loaded successfully!")

# ========== Main Display Area ==========
st.title("🔬 Drug Patent Claim Analyzer")
st.caption("Automated extraction and analysis of solid-form, salt, and amorphous patent claims for your firm's workflow.")

if "patent_df" in st.session_state:
    df = st.session_state["patent_df"]

    filtered_df = df.copy()
    if show_crystalline:
        filtered_df = filtered_df[filtered_df["Crystalline"] == True]
    if show_salt:
        filtered_df = filtered_df[filtered_df["Salt"] == True]
    if show_amorphous:
        filtered_df = filtered_df[filtered_df["Amorphous"] == True]

    st.subheader("📋 Editable Patent Data Table")
    edited_df = st.data_editor(
        filtered_df.drop(columns=["Claims"], errors='ignore'),
        num_rows="dynamic",
        use_container_width=True,
        key="editable_table"
    )

    # Download Button for Excel Export
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

    # Claims Viewer Section
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

# ========== Footer Branding (Optional) ==========
st.markdown("---")
st.caption("© 2025 Barash Law LLC | Confidential | Internal Use Only")
