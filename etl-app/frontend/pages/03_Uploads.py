import streamlit as st
import sys
import pandas as pd
import json
import tempfile
import os

sys.path.append('..')
from api_client import api_client

st.set_page_config(page_title="Upload Data Files", page_icon="📤", layout="wide")

# Check authentication
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.error("Please log in from the main page")
    st.stop()

st.title("📤 Upload Data Files")

# Initialize API client with token - MUST happen before any API calls
if st.session_state.token:
    api_client.set_token(st.session_state.token)
else:
    st.error("No authentication token found. Please log in.")
    st.stop()

tab1, tab2 = st.tabs(["Upload", "History"])

with tab1:
    # File picker
    uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, uploaded_file.name)
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            # Preview file
            preview = api_client.preview_file(file_path)
            if preview:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Rows", preview.get('total_rows', 0))
                with col2:
                    st.metric("Columns", len(preview.get('headers', [])))
                
                cols = preview.get('headers', [])
                detected = preview.get('detected_types', {})
                col_info = ", ".join([f"{c} ({detected.get(c, 'string')})" for c in cols])
                st.caption(f"Columns: {col_info}")
                
                # Sample data
                sample = preview.get('sample_data', [])[:3]
                if sample:
                    st.subheader("Sample Data")
                    st.dataframe(pd.DataFrame(sample), use_container_width=True)
                
                st.divider()
                
                # Target table
                st.subheader("Target Table")
                existing_tables = api_client.list_tables()
                
                create_new = st.checkbox("Create new table", value=len(existing_tables) == 0)
                
                new_table_name = None
                selected_table = None
                
                if create_new:
                    new_table_name = st.text_input(
                        "Table name",
                        value=f"data_{uploaded_file.name.split('.')[0].lower()}"
                    )
                else:
                    if existing_tables:
                        selected_table = st.selectbox("Select table", existing_tables)
                    else:
                        st.warning("No existing tables. Create a new one.")
                        create_new = True
                        new_table_name = st.text_input("Table name", value=f"data_{uploaded_file.name.split('.')[0].lower()}")
                
                st.divider()
                
                # Options
                col1, col2 = st.columns(2)
                with col1:
                    mode = "create" if create_new else "append"
                    st.info(f"Mode: **{mode.upper()}**")
                with col2:
                    add_missing = st.checkbox("Auto-add missing columns")
                
                overrides_text = ""
                with st.expander("Type Overrides (optional)"):
                    overrides_text = st.text_area("", value="", height=60, placeholder="age:integer\nsalary:float")
                
                # Submit
                if st.button("Upload File", type="primary", use_container_width=True):
                    overrides = {}
                    for line in overrides_text.splitlines():
                        if line.strip() and ':' in line:
                            k, v = line.split(':', 1)
                            overrides[k.strip()] = v.strip()
                    
                    target_table = new_table_name if create_new else selected_table
                    
                    upload_request = {
                        "target_table_name": target_table,
                        "column_mappings": [],
                        "skip_rows": 0,
                        "validate_only": False,
                        "mode": mode,
                        "add_missing_columns": add_missing,
                        "column_type_overrides": overrides if overrides else None
                    }
                    
                    result = api_client.upload_file(file_path, upload_request)
                    
                    if result:
                        st.success(f"✅ Upload successful!")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Upload ID", result.get('id'))
                        with col2:
                            st.metric("Records", result.get('row_count', result.get('records_count', 0)))
                        with col3:
                            st.metric("Status", result.get('status'))
                    else:
                        st.error("Upload failed")
            else:
                st.error("Failed to preview file")

with tab2:
    st.subheader("Upload History")
    
    col1, col2 = st.columns(2)
    with col1:
        skip = st.number_input("Skip", min_value=0, value=0)
    with col2:
        limit = st.number_input("Limit", min_value=1, value=20)
    
    uploads = api_client.get_uploads(skip=skip, limit=limit)
    
    if uploads:
        display_data = []
        for upload in uploads:
            display_data.append({
                "ID": upload.get('id'),
                "File": upload.get('file_name', 'N/A'),
                "Status": upload.get('status'),
                "Records": upload.get('row_count', 0),
                "Created": upload.get('created_at', 'N/A')[:10] if upload.get('created_at') else 'N/A'
            })
        
        st.dataframe(pd.DataFrame(display_data), use_container_width=True, hide_index=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            upload_id = st.number_input("View details (ID)", min_value=1, step=1)
        with col2:
            if st.button("Load"):
                st.session_state.view_upload_id = upload_id
        
        if "view_upload_id" in st.session_state:
            upload = api_client.get_upload(st.session_state.view_upload_id)
            if upload:
                st.subheader("Details")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Status", upload.get('status'))
                with col2:
                    st.metric("Records", upload.get('row_count', 0))
                with col3:
                    st.metric("Date", upload.get('created_at', 'N/A')[:10] if upload.get('created_at') else 'N/A')
                
                logs = api_client.get_upload_logs(st.session_state.view_upload_id)
                if logs:
                    with st.expander("Metadata"):
                        st.json(logs)
                
                if upload.get('status') == 'COMPLETED':
                    if st.button("🔄 Rollback"):
                        result = api_client._make_request("POST", f"/uploads/{st.session_state.view_upload_id}/rollback", 
                                                         json={"upload_id": st.session_state.view_upload_id, "reason": "User requested"})
                        if result:
                            st.success("✅ Rolled back")
                        else:
                            st.error("Rollback failed")
            else:
                st.error("Upload not found")
    else:
        st.info("No uploads found")
