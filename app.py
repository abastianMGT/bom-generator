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
    # ⬇️ Use second row as header
    survey_df = pd.read_csv(survey_file, header=1)
    bom_df = pd.read_csv(bom_file)

    st.subheader("📋 Survey Data (with Mount & Model)")
    st.dataframe(survey_df.head())

    st.subheader("🧠 BOM Mapping Logic")
    st.dataframe(bom_df.head())

    try:
        # 🛠 Normalize relevant columns
        survey_df = survey_df.rename(columns={
            "Installation": "Mount_Type",
            "Component Model #": "Model_Number"
        })
        survey_df["Mount_Type"] = survey_df["Mount_Type"].astype(str).str.strip()
        survey_df["Model_Number"] = survey_df["Model_Number"].astype(str).str.strip()

        # 🔗 Merge with BOM reference
        merged = survey_df.merge(
            bom_df,
            on=["Model_Number", "Mount_Type"],
            how="left"
        )

        if merged["Hardware_SKU"].isnull().any():
            st.warning("⚠️ Some combinations were not found in your BOM reference. Check for typos or missing logic.")

        merged["Quantity"] = merged.get("Quantity", 1)
        grouped = merged.groupby(
            ["Model_Number", "Mount_Type", "Hardware_SKU"],
            as_index=False
        )["Quantity"].sum()

        # ✅ Display result
        st.subheader("🔧 Generated Bill of Materials")
        st.dataframe(grouped)

        # 💾 Download BOM
        csv = grouped.to_csv(index=False).encode()
        st.download_button("📥 Download BOM CSV", csv, "generated_bom.csv", "text/csv")
    except Exception as e:
        st.error(f"❌ Error: {e}")
