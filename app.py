import streamlit as st
import pandas as pd

st.title("📦 System Surveyor BOM Generator")

st.markdown("""
Upload your **System Surveyor export** and the **BOM logic CSV**, and get an auto-generated Bill of Materials.
""")

# Upload files
survey_file = st.file_uploader("Upload System Surveyor CSV", type=["csv"])
bom_file = st.file_uploader("Upload Master BOM Mapping CSV", type=["csv"])

if survey_file and bom_file:
    try:
        # Read both files
        survey_df = pd.read_csv(survey_file)
        bom_df = pd.read_csv(bom_file)

        # 🛠 Rename expected columns to match BOM logic format
        survey_df = survey_df.rename(columns={
            "Component Model #": "Model_Number",
            "Mount Bracket": "Mount_Type"
        })
        survey_df["Mount_Type"] = survey_df["Mount_Type"].astype(str).str.strip()
        survey_df["Model_Number"] = survey_df["Model_Number"].astype(str).str.strip()

        st.subheader("📋 Survey Data (Mapped)")
        st.dataframe(survey_df[["Model_Number", "Mount_Type"]].head())

        st.subheader("🧠 BOM Mapping Logic")
        st.dataframe(bom_df.head())

        # 🔗 Merge survey data with BOM reference
        merged = survey_df.merge(
            bom_df,
            on=["Model_Number", "Mount_Type"],
            how="left"
        )

        # ✅ Show warning if any mappings were not found
        if merged["Hardware_SKU"].isnull().any():
            st.warning("⚠️ Some combinations were not found in your BOM mapping file.")

        # Default quantity to 1 if not defined
        merged["Quantity"] = merged.get("Quantity", 1)

        # 📦 Final grouped BOM
        grouped = merged.groupby(
            ["Model_Number", "Mount_Type", "Hardware_SKU"],
            as_index=False
        )["Quantity"].sum()

        st.subheader("🔧 Generated Bill of Materials")
        st.dataframe(grouped)

        # 💾 Download CSV
        csv = grouped.to_csv(index=False).encode()
        st.download_button("📥 Download BOM CSV", csv, "generated_bom.csv", "text/csv")

    except Exception as e:
        st.error(f"❌ An error occurred: {e}")
