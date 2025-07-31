# 🔬 The Orange Bookinator

**Automated extraction and analysis of Orange Book-listed patents for novel drug approvals.**

The Orange Bookinator is a Streamlit-based tool designed for pharmaceutical patent analysts and regulatory professionals. It allows users to fetch, clean, and explore therapeutic equivalence claims associated with novel FDA-approved drugs, including solid-form classifications like crystalline, salt, and amorphous.

---

## 🚀 Features

- 📅 Select a single FDA approval year or a custom range (2021–2025)
- 🔎 Scrape and merge data on approved drugs and their Orange Book patents
- 🧠 Identify key claim types: **Crystalline**, **Salt**, **Amorphous**
- 🧾 Review and format full patent claim language
- 📥 Download a clean, editable Excel report
- ✏️ Inline editing of solid-form classifications for internal workflows

---

## 🖥️ Live App

> [🔗 Launch on Streamlit Cloud](https://orangebook.streamlit.app)

---

## 🧰 How to Use

1. **Run Locally**
   ```bash
   pip install -r requirements.txt
   streamlit run app.py
