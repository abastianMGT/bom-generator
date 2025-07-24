import streamlit as st
import pandas as pd

st.title("📦 System Surveyor BOM Generator")

st.markdown("""
Upload your **System Surveyor export** and the **BOM logic CSV**, and get a final flat Bill of Materials including both camera SKUs and hardware SKUs, grouped and totaled correctly.
""")

# Upload files
survey_file = st.file_uploader("Upload System Surveyor CSV", type=["csv"])
bom_file = st.file_uploader("Upload Master BOM Mapping CSV", type=["csv"])

if survey_file and bom_file:
    try:
        # Load input files
        survey_df = pd.read_csv(survey_file)
        bom_df = pd.read_csv(bom_file)

        # Normalize and rename columns
        survey_df = survey_df.rename(columns={
            "Component Model #": "Model_Number",
            "Mount Bracket": "Mount_Type"
        })
        survey_df["Mount_Type"] = survey_df["Mount_Type"].astype(str).str.strip()
        survey_df["Model_Number"] = survey_df["Model_Number"].astype(str).str.strip()

        # Count how many times each model+mount pair occurs
        grouped_cameras = survey_df.groupby(["Model_Number", "Mount_Type"]).size().reset_index(name="Camera_Quantity")

        # Merge with BOM logic
        merged = grouped_cameras.merge(
            bom_df,
            on=["Model_Number", "Mount_Type"],
            how="left"
        )

        if merged["Hardware_SKU"].isnull().any():
            st.warning("⚠️ Some model/mount pairs were not found in the BOM mapping file.")

        # Scale mount hardware quantity by camera quantity
        merged["Hardware_Quantity"] = merged["Camera_Quantity"] * merged.get("Quantity", 1)

        # Step 1: Add camera rows separately
        camera_rows = grouped_cameras.copy()
        camera_rows["Hardware_SKU"] = camera_rows["Model_Number"]
        camera_rows["Quantity"] = camera_rows["Camera_Quantity"]
        camera_rows = camera_rows[["Hardware_SKU", "Quantity"]]

        # Step 2: Add mount hardware rows with correct quantity
        hardware_rows = merged[["Hardware_SKU", "Hardware_Quantity"]].rename(columns={"Hardware_Quantity": "Quantity"})

        # Step 3: Combine and group totals
        final_bom = pd.concat([camera_rows, hardware_rows], ignore_index=True)
        final_flat = final_bom.groupby("Hardware_SKU", as_index=False)["Quantity"].sum()

        # Show result
        st.subheader("🔧 Final Flat BOM with Quantities")
        st.dataframe(final_flat)

        # Download CSV
        csv = final_flat.to_csv(index=False).encode()
        st.download_button("📥 Download Final BOM CSV", csv, "final_flat_bom.csv", "text/csv")

    except Exception as e:
        st.error(f"❌ An error occurred: {e}")
