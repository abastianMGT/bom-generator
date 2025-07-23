import streamlit as st
import pandas as pd

st.title("📦 System Surveyor BOM Generator")

st.markdown("""
Upload your **System Surveyor export** and the **BOM mapping CSV**, and get a flat, totalled Bill of Materials by SKU.
""")

# Upload files
survey_file = st.file_uploader("Upload System Surveyor CSV", type=["csv"])
bom_file = st.file_uploader("Upload BOM Mapping CSV", type=["csv"])

if survey_file and bom_file:
    try:
        # Load data
        survey_df = pd.read_csv(survey_file)
        bom_df = pd.read_csv(bom_file)

        # Rename expected columns
        survey_df = survey_df.rename(columns={
            "Component Model #": "Model_Number",
            "Mount Bracket": "Mount_Type"
        })
        survey_df["Mount_Type"] = survey_df["Mount_Type"].astype(str).str.strip()
        survey_df["Model_Number"] = survey_df["Model_Number"].astype(str).str.strip()

        # Merge survey with BOM mapping
        merged = survey_df.merge(
            bom_df,
            on=["Model_Number", "Mount_Type"],
            how="left"
        )

        if merged["Hardware_SKU"].isnull().any():
            st.warning("⚠️ Some combinations were not found in your BOM mapping file.")

        # Default quantity to 1 if not provided
        merged["Quantity"] = merged.get("Quantity", 1)

        # Final flat BOM by part totals
        final_bom = merged.groupby("Hardware_SKU", as_index=False)["Quantity"].sum()

        st.subheader("🔧 Final Flat Bill of Materials (Summed by SKU)")
        st.dataframe(final_bom)

        # Download button
        csv = final_bom.to_csv(index=False).encode()
        st.download_button("📥 Download Flat BOM CSV", csv, "final_flat_bom.csv", "text/csv")

    except Exception as e:
        st.error(f"❌ An error occurred: {e}")
