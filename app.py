import streamlit as st
import pandas as pd

from utilis import clean_data, convert_dtype, display_df, remove_duplicates, upload_file, load_file, fill_null

if "data" not in st.session_state:
    st.session_state.data = None 
    
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

if "selected_file_index" not in st.session_state:
    st.session_state.selected_file_index = 0
    
def main():
    st.title("Tabula Flow")
    st.subheader("CSV/EXCEL File Formatter")

    if st.button("Clear Files"):
        st.session_state.data = None
        st.rerun()
        
    data = upload_file()
    # sets data and session state data to the uploaded file,
    # if data is not already set. This allows us to keep the original data 
    # in session state while we perform cleaning operations on the data variable.
    
    if data is not None and st.session_state.data is None:
        st.session_state.original_data = data 
        st.session_state.data = data.copy()  
        # Use copy to avoid modifying the original data in session state
        if isinstance(data, list):
            
            fileindex = st.selectbox(
                "Select File", 
                range(len(data)), 
                 key="file_selector"
            )
            st.session_state.data = data[fileindex]
        else:
            st.session_state.data = data
            
    with st.sidebar:
        st.sidebar.title("⚙️ Data Tools")
            # Add your data cleaning tools here, e.g., remove duplicates, fill nulls, etc.
            
        clean_nulls = st.button("Remove NA ")
        if clean_nulls and "data" in st.session_state:
                st.session_state.data = clean_data(st.session_state.data)
                
        remove_dupes = st.button("Remove Duplicates")
        if remove_dupes and "data" in st.session_state:
                st.session_state.data = remove_duplicates(
                    st.session_state.data)
                
        fill_value = st.text_input("Fill NA with: ")
        fill_nulls = st.button("Fill NA")
        if fill_nulls and "data" in st.session_state and fill_value:
                st.session_state.data = fill_null(
                    st.session_state.data, fill_value)
                
        
        st.subheader("Convert Data Type")

        if st.session_state.data is not None:

            columns = st.session_state.data.columns.tolist()

            dtype_column = st.selectbox(    
            "Select column",
            columns,
            key="dtype_column"
        )

        dtype_option = st.selectbox(
            "Convert to",
            ["int", "float", "string", "datetime"],
            key="dtype_option"
        )

        convert_button = st.button("Convert Type")

        if convert_button:
            st.session_state.data = convert_dtype(
            st.session_state.data,
            dtype_column,
            dtype_option
            )        
        
        
    if data is not None and st.session_state.data is not None:
            display_df(st.session_state.data)
        

if __name__ == "__main__":
    main()