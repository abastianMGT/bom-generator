import streamlit as st
import pandas as pd

st.title("📦 System Surveyor BOM Generator")

st.markdown("""
Upload your **System Surveyor export** and the **BOM mapping CSV**, and generate a flat Bill of Materials with correct quantities for both camera and hardware SKUs.
""")

# Upload files
survey_file = st.file_uploader("Upload System Surveyor CSV", type=["csv"])
bom_file = st.file_uploader("Upload Master BOM Mapping CSV", type=["csv"])

if survey_file and bom_file:
    try:
        # Load input files
        survey_df = pd.read_csv(survey_file)
        bom_df = pd.read_csv(bom_file)

        # Normalize column names
        survey_df = survey_df.rename(columns={
            "Component Model #": "Model_Number",
            "Mount Bracket": "Mount_Type"
        })
        survey_df["Mount_Type"] = survey_df["Mount_Type"].astype(str).str.strip()
        survey_df["Model_Number"] = survey_df["Model_Number"].astype(str).str.strip()

        # Step 1: Count how many times each (Model_Number, Mount_Type) occurs
        grouped_cameras = survey_df.groupby(["Model_Number", "Mount_Type"]).size().reset_index(name="Camera_Count")

        # Step 2: Merge with BOM logic
        merged = grouped_cameras.merge(
            bom_df,
            on=["Model_Number", "Mount_Type"],
            how="left"
        )

        if merged["Hardware_SKU"].isnull().any():
            st.warning("⚠️ Some model/mount pairs were not found in the BOM mapping file.")

        # Step 3: Calculate hardware quantity scaled by camera count
        merged["Hardware_Quantity"] = merged["Camera_Count"] * merged.get("Quantity", 1)

        # Step 4: Get hardware rows
        hardware_rows = merged[["Hardware_SKU", "Hardware_Quantity"]].rename(
            columns={"Hardware_Quantity": "Quantity"}
        )

        # Step 5: Get camera rows with their counts
        camera_rows = grouped_cameras[["Model_Number", "Camera_Count"]].rename(
            columns={"Model_Number": "Hardware_SKU", "Camera_Count": "Quantity"}
        )

        # Step 6: Combine both and sum quantities for duplicate SKUs
        final_bom = pd.concat([camera_rows, hardware_rows], ignore_index=True)
        final_flat = final_bom.groupby("Hardware_SKU", as_index=False)["Quantity"].sum()

        # Display output
        st.subheader("🔧 Final Flat BOM")
        st.dataframe(final_flat)

        # Downloadable CSV
        csv = final_flat.to_csv(index=False).encode()
        st.download_button("📥 Download Final BOM CSV", csv, "final_flat_bom.csv", "text/csv")

    except Exception as e:
        st.error(f"❌ An error occurred: {e}")
