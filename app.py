
import streamlit as st
import pandas as pd

st.title("📦 System Surveyor BOM Generator")

st.markdown("""
Upload your **System Surveyor export** and the **BOM logic CSV**, and get an auto-generated Bill of Materials.
""")

# Upload system surveyor file
survey_file = st.file_uploader("Upload System Surveyor CSV", type=["csv"])
bom_file = st.file_uploader("Upload Master BOM Mapping CSV", type=["csv"])

if survey_file and bom_file:
    survey_df = pd.read_csv(survey_file)
    bom_df = pd.read_csv(bom_file)

    st.subheader("📋 Survey Data")
    st.dataframe(survey_df.head())

    st.subheader("🧠 Mapping Logic (BOM Reference)")
    st.dataframe(bom_df.head())

    try:
        # Use 'Mount Bracket' column as Mount_Type
        survey_df = survey_df.rename(columns={"Mount Bracket": "Mount_Type"})
        survey_df["Mount_Type"] = survey_df["Mount_Type"].astype(str).str.strip()
        survey_df["Model_Number"] = survey_df["Model_Number"].astype(str).str.strip()

        merged = survey_df.merge(
            bom_df,
            on=["Model_Number", "Mount_Type"],
            how="left"
        )

        if merged["Hardware_SKU"].isnull().any():
            st.warning("Some combinations were not found in your BOM reference.")

        merged["Quantity"] = merged.get("Quantity", 1)
        grouped = merged.groupby(["Model_Number", "Mount_Type", "Hardware_SKU"], as_index=False)["Quantity"].sum()

        st.subheader("🔧 Generated BOM")
        st.dataframe(grouped)

        csv = grouped.to_csv(index=False).encode()
        st.download_button("📥 Download BOM CSV", csv, "generated_bom.csv", "text/csv")
    except Exception as e:
        st.error(f"Error: {e}")
