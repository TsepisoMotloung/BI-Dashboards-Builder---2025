import streamlit as st
import sys
import json
sys.path.append('..')
from api_client import api_client

st.set_page_config(page_title="Data Models", page_icon="📊")

# Check authentication
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.error("Please log in from the main page")
    st.stop()

st.header("📊 Data Model Management")

# Initialize API client with token
if st.session_state.token:
    api_client.set_token(st.session_state.token)

tab1, tab2, tab3 = st.tabs(["View Models", "Create Model", "Manage Model"])

with tab1:
    st.subheader("All Data Models")
    
    col1, col2 = st.columns(2)
    with col1:
        skip = st.number_input("Skip", min_value=0, value=0, key="view_skip")
    with col2:
        limit = st.number_input("Limit", min_value=1, value=50, key="view_limit")
    
    models = api_client.get_data_models(skip=skip, limit=limit)
    
    if models:
        # Convert to displayable format
        display_data = []
        for model in models:
            display_data.append({
                "ID": model.get('id'),
                "Name": model.get('name'),
                "Description": model.get('description', ''),
                "Organization ID": model.get('organization_id'),
                "Created": model.get('created_at', 'N/A')[:10] if model.get('created_at') else 'N/A'
            })
        
        st.dataframe(display_data, use_container_width=True)
    else:
        st.info("No data models found")

with tab2:
    st.subheader("Create New Data Model")
    
    with st.form("create_model_form"):
        name = st.text_input("Model Name")
        description = st.text_area("Description")
        org_id = st.number_input("Organization ID", min_value=1, value=1)
        
        st.write("### Fields")
        num_fields = st.number_input("Number of fields", min_value=1, value=1)
        
        fields = []
        for i in range(num_fields):
            col1, col2, col3 = st.columns(3)
            with col1:
                field_name = st.text_input(f"Field {i+1} Name", key=f"field_name_{i}")
            with col2:
                field_type = st.selectbox(f"Field {i+1} Type", 
                                         ["string", "integer", "float", "date", "datetime", "boolean", "text"],
                                         key=f"field_type_{i}")
            with col3:
                is_required = st.checkbox(f"Required", key=f"field_req_{i}")
            
            if field_name:
                fields.append({
                    "name": field_name,
                    "type": field_type,
                    "required": is_required
                })
        
        submitted = st.form_submit_button("Create Model")
        
        if submitted:
            if name and fields:
                result = api_client.create_data_model(
                    name=name,
                    description=description if description else None,
                    fields=fields
                )
                if result:
                    st.success(f"Data model created successfully! ID: {result.get('id')}")
                else:
                    st.error("Failed to create data model")
            else:
                st.warning("Please enter a model name and at least one field")

with tab3:
    st.subheader("Manage Existing Data Model")
    
    model_id = st.number_input("Model ID", min_value=1, key="manage_model_id")
    
    if st.button("Load Model"):
        model = api_client.get_data_model(model_id)
        if model:
            st.session_state.selected_model = model
        else:
            st.error("Model not found")
    
    if "selected_model" in st.session_state:
        model = st.session_state.selected_model
        
        st.write("### Model Details")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Name:** {model.get('name')}")
            st.write(f"**Organization ID:** {model.get('organization_id')}")
        with col2:
            st.write(f"**Created:** {model.get('created_at', 'N/A')[:10]}")
            st.write(f"**Updated:** {model.get('updated_at', 'N/A')[:10]}")
        
        st.write(f"**Description:** {model.get('description', 'N/A')}")
        
        if model.get('fields'):
            st.write("**Fields:**")
            st.json(model.get('fields'))
        
        st.divider()
        
        with st.form("update_model_form"):
            new_name = st.text_input("Model Name", value=model.get('name', ''))
            new_description = st.text_area("Description", value=model.get('description', ''))
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Update Model"):
                    result = api_client.update_data_model(
                        model_id,
                        name=new_name,
                        description=new_description
                    )
                    if result:
                        st.success("Model updated successfully!")
                        del st.session_state.selected_model
                        st.rerun()
                    else:
                        st.error("Failed to update model")
            
            with col2:
                if st.form_submit_button("Delete Model", type="secondary"):
                    if api_client.delete_data_model(model_id):
                        st.success("Model deleted successfully!")
                        del st.session_state.selected_model
                        st.rerun()
                    else:
                        st.error("Failed to delete model")
