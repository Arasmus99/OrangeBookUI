import streamlit as st
import pandas as pd
from helpers.generate_merged_df import generate_merged_df
from helpers.formatting import format_claims

st.set_page_config(page_title="Drug Patent Claim Analyzer", layout="wide", initial_sidebar_state="expanded")

st.sidebar.image("firm_logo.png", use_container_width=True)
st.sidebar.markdown("---")

mode = st.sidebar.radio("Select Data Mode:", ["Single Year", "Range"], horizontal=True)

if mode == "Single Year":
    year = st.sidebar.number_input("Enter FDA Approval Year", min_value=2021, max_value=2025, value=2025)
else:
    year_range = st.sidebar.slider("Select FDA Approval Year Range", min_value=2021, max_value=2025, value=(2021, 2025))

if st.sidebar.button("Fetch and Analyze Patents"):
    with st.spinner("Fetching and processing patent data. Please wait..."):
        try:
            if mode == "Single Year":
                df = generate_merged_df(year)
            else:
                dfs = [generate_merged_df(yr) for yr in range(year_range[0], year_range[1] + 1)]
                df = pd.concat(dfs, ignore_index=True)
            st.session_state["patent_df"] = df
            st.success("Data loaded successfully.")
        except Exception as e:
            st.error(f"Data fetch failed: {e}")

st.sidebar.markdown("### Filter Results By")
show_crystalline = st.sidebar.checkbox("Show Crystalline", value=False)
show_salt = st.sidebar.checkbox("Show Salt", value=False)
show_amorphous = st.sidebar.checkbox("Show Amorphous", value=False)

st.title("🔬 The Orange Bookinator")
st.caption("Automated extraction and analysis of solid-form, salt, and amorphous patent claims.")

if "patent_df" in st.session_state:
    df = st.session_state["patent_df"].copy()
    filtered_df = df.copy()

    if show_crystalline:
        filtered_df = filtered_df[filtered_df["Crystalline"] == True]
    if show_salt:
        filtered_df = filtered_df[filtered_df["Salt"] == True]
    if show_amorphous:
        filtered_df = filtered_df[filtered_df["Amorphous"] == True]

    st.subheader("📋 Editable Patent Data Table")
    edited_df = st.data_editor(filtered_df.drop(columns=["Claims"], errors='ignore'), num_rows="dynamic", use_container_width=True, key="editable_table")

    if not edited_df.empty:
        for idx, row in edited_df.iterrows():
            patent_number = row["Patent Number"]
            mask = df["Patent Number"] == patent_number
            for col in ["Crystalline", "Salt", "Amorphous"]:
                if col in row and pd.notna(row[col]):
                    df.loc[mask, col] = row[col]
        st.session_state["patent_df"] = df

    filename = f"Patent_Data_{year}.xlsx" if mode == "Single Year" else f"Patent_Data_{year_range[0]}_{year_range[1]}.xlsx"
    buffer = pd.ExcelWriter(filename, engine="xlsxwriter")
    edited_df.to_excel(buffer, index=False, sheet_name="Patent Data")
    buffer.close()

    with open(filename, "rb") as file:
        st.download_button("📥 Download Table as Excel", data=file, file_name=filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.subheader("📑 View Patent Claims")
    selected_patent = st.selectbox("Select Patent Number to View Claims:", edited_df["Patent Number"].dropna().unique())
    selected_row = df[df["Patent Number"] == selected_patent]
    if not selected_row.empty:
        raw_claims = selected_row["Claims"].values[0]
        formatted_claims = format_claims(raw_claims)
        st.text_area("Patent Claims:", value=formatted_claims, height=700)
else:
    st.info("Use the sidebar to fetch and analyze patent data for the selected year or range.")

st.markdown("---")
st.caption("© 2025 Barash Law LLC | Confidential | Internal Use Only")
