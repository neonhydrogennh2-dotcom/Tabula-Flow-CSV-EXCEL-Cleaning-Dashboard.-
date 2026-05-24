import pandas as pd
import streamlit as st
import os
import logging
import io 

# App Handeling 

def reset_app():

    st.session_state.pop("data", None)
    st.session_state.pop("uploaded_df", None)
    st.session_state.pop("current_df", None)

    if "uploader_version" not in st.session_state:
        st.session_state.uploader_version = 0

    st.session_state.uploader_version += 1

    st.rerun()

# File Handeling 

def upload_file():
    try:
        if "uploader_version" not in st.session_state:
            st.session_state.uploader_version = 0

        uploaded_file = st.file_uploader(
            "Upload your file",
            key=f"files_upload_{st.session_state.uploader_version}",
            type=["csv", "xlsx"], 
            max_upload_size= 5,
            accept_multiple_files=True
        )

        if uploaded_file:
            #data = load_file(uploaded_file)
            dfs = load_multiple_files(uploaded_file)
            st.session_state.uploaded_dfs = dfs
            st.session_state.file_names = [f.name for f in uploaded_file]
            if dfs is not None:
                return dfs
            
    except Exception as e:
        logging.error(e)


def display_df(df):
    if df is None:
            return
            

            #st.subheader("File Data")

    cols1, cols2, cols3, cols4 = st.columns(4)

    cols1.metric("Rows", df.shape[0])
    cols2.metric("Columns", df.shape[1])
    cols3.metric("Missing Values", df.isna().sum().sum()) # Mark missing values 
             # Count per  column # Total count
    cols4.metric("Duplicate Values", df.duplicated(keep=False).sum())
    

    st.subheader("Data Preview")
    st.dataframe(df)

    st.subheader("Column Names")
    st.table(pd.DataFrame({
            "Column Name": df.columns,
            "Data Type": df.dtypes.values
            }))

    if "current_df" in st.session_state:

        csv = st.session_state.current_df.to_csv(index=False).encode("utf-8")

        st.download_button(
        label="Download CSV",
        data=csv,
        file_name="cleaned_data.csv",
        mime="text/csv"
        )

    if "current_df" in st.session_state:

        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            st.session_state.current_df.to_excel(writer, index=False)

        st.download_button(
        label="Download Excel",
        data=buffer.getvalue(),
        file_name="cleaned_data.xlsx",
        mime="application/vnd.ms-excel"
        )


def load_file(files):
    max_size = 5 * 1024 * 1024  # 5MB

    dfs = []

    for file in files:


        ext = os.path.splitext(file.name)[1].lower()

        if file.size > max_size:
            st.error(f"{file.name} exceeds size limit")
            return None

        try:
            if ext == ".csv":
                data = pd.read_csv(file)

            elif ext == ".xlsx":
                data = pd.read_excel(file)

            else:
                st.error("Unsupported file type")
                return None

            st.success("File Uploaded Successfully")
            dfs.append(data)
            return dfs

        except Exception as e:
            st.error("Error reading file")
            logging.error(e)
            return None
    
def load_multiple_files(uploaded_files):

    dfs = []

    for file in uploaded_files:

        ext = os.path.splitext(file.name)[1].lower()

        if ext == ".csv":
            df = pd.read_csv(file)

        elif ext == ".xlsx":
            df = pd.read_excel(file)

        else:
            st.warning(f"Unsupported file: {file.name}")
            continue

        dfs.append(df)

    return dfs

#Data Cleaning

def clean_data(df):
    st.write("Before:", df.shape[0])

    df = df.copy()
    df.replace("", pd.NA, inplace=True)
    df.dropna(inplace=True)

    st.write("After:", df.shape[0])
    return df 


def remove_duplicates(df):
    df = df.copy()
    df.drop_duplicates(inplace=True)
    return df 

def fill_null(df, value):
    df = df.copy()
    return df.fillna(value)
    
def rename_columns(df, old_name, new_name): 
    df = df.copy()
    return df.rename(columns={old_name:new_name})


def convert_dtype(df, column, dtype):
    df = df.copy()

    try:
        if dtype == "int":
            df[column] = pd.to_numeric(df[column], errors="coerce").astype(int)

        elif dtype == "float":
            df[column] = pd.to_numeric(df[column], errors="coerce")

        elif dtype == "string":
            df[column] = df[column].astype("string")

        elif dtype == "datetime":
            df[column] = pd.to_datetime(df[column], errors="coerce")

    except Exception as e:
        st.error(f"Conversion failed: {e}")

    return df


def merge_files(dfs):
    try: 
        merged_df = pd.concat(dfs, ignore_index=True)
        return merged_df
    except Exception as e: 
        st.error(f"Merge failed: {e}")
        return None