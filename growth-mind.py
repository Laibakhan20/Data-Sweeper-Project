import streamlit as st
import pandas as pd
import os
from io import BytesIO

st.set_page_config(page_title="Data Sweeper", layout="wide")


# custom css
st.markdown(
    """ 
    <style>
    .stApp{
        background-color : white ;
        color : black ;
    }
    </style>
    """,
    unsafe_allow_html = True
)

# title and description
st.title("DataSweeper")
st.write("A simple web app to clean and preprocess data")

# file uploader
uploaded_files = st.file_uploader("upload your files (accepts csv or excel):", type=["csv", "xlsx"], accept_multiple_files=(True))
     
if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        # Read file based on extension
        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"Unsupported file type: {file_ext}")
            continue

        st.write(f"### Preview of {file.name}")
        st.dataframe(df.head())

        # Data Cleaning Options
        if st.checkbox(f"Clean data for {file.name}"):  
            col1, col2 = st.columns(2)

            with col1:
                if st.checkbox(f"Remove duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.success("Duplicates removed!")

            with col2:
                if st.button(f"Fill missing values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=["number"]).columns
                    if len(numeric_cols) > 0:
                        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                        st.success("Missing values filled!")
                    else:
                        st.warning("No numeric columns found to fill missing values.")

            # Column selection
            st.subheader("Select columns to keep:")
            columns = st.multiselect(f"Choose columns for {file.name}", df.columns, default=df.columns)
            df = df[columns]

            # Data Visualization Section
            st.subheader(f"Data Visualization for {file.name}")
            numeric_cols = df.select_dtypes(include=["number"]).columns

            if len(numeric_cols) > 0:  
                selected_column = st.selectbox(f"Select a numeric column to visualize for {file.name}", numeric_cols)

                chart_type = st.radio("Select chart type:", ["Bar Chart", "Line Chart"], key=file.name)

                if st.button(f"Generate Visualization for {file.name}"):
                    st.write(f"### {chart_type} of {selected_column}")

                    if chart_type == "Bar Chart":
                        st.bar_chart(df[selected_column])
                    elif chart_type == "Line Chart":
                        st.line_chart(df[selected_column])
            else:
                st.warning("No numeric columns available for visualization.")

        # File Conversion Options
        st.subheader("Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=f"convert_{file.name}")

        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()

            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"
            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False, engine="openpyxl")  # Ensure openpyxl is used for Excel
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            buffer.seek(0)

            st.download_button(
                label=f"Download {file.name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type
            )

st.success("All files processed successfully!")