import streamlit as st
from helpers.generate_merged_df import generate_merged_df
import io
import pandas as pd

st.set_page_config(layout="wide")
st.title("Drug Patent Claim Analyzer")

# User selects the year
year = st.number_input("Enter FDA Approval Year", min_value=2000, max_value=2100, value=2025)

if st.button("Fetch Data"):
    with st.spinner("Loading and parsing data. This may take a minute..."):
        df = generate_merged_df(year)
        st.session_state["patent_df"] = df.copy()
        st.success("Data loaded successfully!")

# Display data if available
if "patent_df" in st.session_state:
    df = st.session_state["patent_df"]

    # Sidebar filters
    st.sidebar.header("Filter by Patent Type")
    show_crystalline = st.sidebar.checkbox("Crystalline", value=False)
    show_salt = st.sidebar.checkbox("Salt", value=False)
    show_amorphous = st.sidebar.checkbox("Amorphous", value=False)

    filtered_df = df.copy()
    if show_crystalline:
        filtered_df = filtered_df[filtered_df["Crystalline"] == True]
    if show_salt:
        filtered_df = filtered_df[filtered_df["Salt"] == True]
    if show_amorphous:
        filtered_df = filtered_df[filtered_df["Amorphous"] == True]

    # Drop 'Claims' column for display only
    display_df = filtered_df.drop(columns=["Claims"], errors="ignore")

    st.markdown("### Editable Patent Data Table")
    edited_df = st.data_editor(
        display_df,
        num_rows="dynamic",
        use_container_width=True,
        key="editable_table"
    )

    # Update the main df with edited changes to reflect checkbox edits permanently
    for col in ["Crystalline", "Salt", "Amorphous"]:
        if col in edited_df.columns:
            df[col] = edited_df[col]
    st.session_state["patent_df"] = df

    # Download button for Excel export
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        edited_df.to_excel(writer, index=False, sheet_name="Patent Data")
    st.download_button(
        label="📥 Download Table as Excel",
        data=buffer.getvalue(),
        file_name="drug_patent_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.markdown("### View Claims for a Selected Patent")
    selected_patent = st.selectbox("Select Patent Number", filtered_df["Patent Number"].dropna().unique())
    selected_row = df[df["Patent Number"] == selected_patent]
    if not selected_row.empty:
        st.text_area("Patent Claims", selected_row["Claims"].values[0], height=300)
