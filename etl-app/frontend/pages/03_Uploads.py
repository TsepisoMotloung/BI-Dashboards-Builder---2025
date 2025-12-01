import streamlit as st
import sys
import pandas as pd
sys.path.append('..')
from api_client import api_client

st.set_page_config(page_title="Upload Management", page_icon="📤")

# Check authentication
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.error("Please log in from the main page")
    st.stop()

st.header("📤 Upload Management")

# Initialize API client with token
if st.session_state.token:
    api_client.set_token(st.session_state.token)

tab1, tab2 = st.tabs(["View Uploads", "Upload File"])

with tab1:
    st.subheader("All Uploads")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        skip = st.number_input("Skip", min_value=0, value=0)
    with col2:
        limit = st.number_input("Limit", min_value=1, value=50)
    
    uploads = api_client.get_uploads(skip=skip, limit=limit)
    
    if uploads:
        # Convert to displayable format
        display_data = []
        for upload in uploads:
            display_data.append({
                "ID": upload.get('id'),
                "File Name": upload.get('file_name', 'N/A'),
                "Status": upload.get('status', 'unknown'),
                "Data Model ID": upload.get('data_model_id'),
                "Created": upload.get('created_at', 'N/A')[:10] if upload.get('created_at') else 'N/A',
                "Records": upload.get('row_count', 0)
            })
        
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True)
        
        # Detail view
        upload_id = st.number_input("View upload details (ID)", min_value=1)
        if st.button("Load Details"):
            upload = api_client.get_upload(upload_id)
            if upload:
                st.write("### Upload Details")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Status", upload.get('status', 'N/A'))
                with col2:
                    st.metric("Records", upload.get('row_count', 0))
                with col3:
                    st.metric("Data Model ID", upload.get('data_model_id', 'N/A'))
                
                st.write("**Upload Logs:**")
                logs = api_client.get_upload_logs(upload_id)
                if logs:
                    log_df = pd.DataFrame(logs)
                    st.dataframe(log_df, use_container_width=True)
                else:
                    st.info("No logs found")
            else:
                st.error("Upload not found")
    else:
        st.info("No uploads found")

with tab2:
    st.subheader("Upload New File")
    
    # Get available data models
    models = api_client.get_data_models(limit=100)
    model_options = {m.get('name', f"Model {m.get('id')}"): m.get('id') for m in models}
    
    if not model_options:
        st.warning("No data models available. Please create a data model first.")
    else:
        with st.form("upload_form"):
            selected_model = st.selectbox("Select Data Model", list(model_options.keys()))
            uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx', 'xls', 'json'])
            
            submitted = st.form_submit_button("Upload File")
            
            if submitted:
                if uploaded_file:
                    # Save file temporarily
                    import tempfile
                    import os
                    
                    with tempfile.TemporaryDirectory() as tmpdir:
                        file_path = os.path.join(tmpdir, uploaded_file.name)
                        with open(file_path, 'wb') as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Upload file
                        model_id = model_options[selected_model]
                        result = api_client.upload_file(file_path, model_id)
                        
                        if result:
                            st.success(f"File uploaded successfully! Upload ID: {result.get('id')}")
                            st.info(f"Status: {result.get('status', 'processing')}")
                        else:
                            st.error("Failed to upload file")
                else:
                    st.warning("Please select a file")
