import streamlit as st
from helpers.fda import scrape_fda_novel_approvals
from helpers.orange_book import load_orange_book
from helpers.patents import parse_patent_google
from helpers.merge import merge_and_process

st.set_page_config(layout="wide")
st.title("FDA Novel Drug Patent Explorer")

# Step 1: User selects a year
year = st.number_input("Enter FDA Novel Drug Approval Year:", min_value=2015, max_value=2025, value=2025, step=1)

# Step 2: Trigger data generation
data_loaded = st.button("🔍 Load Drug & Patent Data")

if data_loaded:
    with st.spinner("Loading and parsing data. This may take a minute..."):
        df = generate_merged_df(year)

        # Set default False for DS/DP/SF/Crystalline/Salt if not present
        for col in ["DS", "DP", "SF", "Crystalline", "Salt", "Amorphous"]:
            if col not in df.columns:
                df[col] = False

        # Allow user filtering
        st.sidebar.header("Filter Options")
        show_crystalline = st.sidebar.checkbox("Only Crystalline", value=False)
        show_salt = st.sidebar.checkbox("Only Salt", value=False)
        show_amorphous = st.sidebar.checkbox("Only Amorphous", value=False)

        filtered_df = df.copy()
        if show_crystalline:
            filtered_df = filtered_df[filtered_df["Crystalline"] == True]
        if show_salt:
            filtered_df = filtered_df[filtered_df["Salt"] == True]
        if show_amorphous:
            filtered_df = filtered_df[filtered_df["Amorphous"] == True]

        # Display and allow edits
        st.subheader("💊 Drug and Patent Table")
        edited_df = st.data_editor(filtered_df, num_rows="dynamic", use_container_width=True)

        # Step 3: Patent number click & claim view
        selected_patent = st.selectbox("Select a Patent Number to View Claims:", df["Patent Number"].dropna().unique())
        if selected_patent:
            with st.spinner("Fetching claims from Google Patents..."):
                claims = get_claims(selected_patent)
                st.subheader(f"📜 Claims for US Patent {selected_patent}")
                st.markdown(claims or "_No claims found._")
