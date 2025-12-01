import streamlit as st
import sys
sys.path.append('..')
from api_client import api_client

st.set_page_config(page_title="Organization", page_icon="🏢", layout="wide")

# Check authentication
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.error("Please log in from the main page")
    st.stop()

st.header("🏢 Organization Management")

# Initialize API client with token
if st.session_state.token:
    api_client.set_token(st.session_state.token)

tab1, tab2, tab3 = st.tabs(["View Organizations", "Create Organization", "Manage Organization"])

with tab1:
    st.subheader("All Organizations")
    
    orgs = api_client.get_organizations()
    
    if orgs:
        st.write(f"Showing {len(orgs)} organizations")

        for o in orgs:
            expand_key = f"expand_org_{o.get('id')}"
            if expand_key not in st.session_state:
                st.session_state[expand_key] = False
            
            cols = st.columns([1, 3, 2, 2, 2, 1.5])
            with cols[0]:
                st.write(o.get('id'))
            with cols[1]:
                st.write(o.get('name'))
            with cols[2]:
                st.write(o.get('org_unit_type', 'N/A'))
            with cols[3]:
                st.write(o.get('parent_id') or 'Root')
            with cols[4]:
                created = o.get('created_at')
                st.write(created[:10] if created else 'N/A')
            with cols[5]:
                col_buttons = st.columns(2)
                with col_buttons[0]:
                    if st.button("Edit", key=f"edit_org_{o.get('id')}"):
                        st.session_state[expand_key] = not st.session_state[expand_key]
                with col_buttons[1]:
                    if st.button("Del", key=f"del_org_{o.get('id')}"):
                        st.session_state[f"confirm_del_org_{o.get('id')}"] = True
                if st.session_state.get(f"confirm_del_org_{o.get('id')}", False):
                    st.warning(f"⚠️ Confirm deletion of Organization {o.get('id')} ({o.get('name')})? All departments, roles, and users will be deleted. This cannot be undone.")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Yes, Delete All", key=f"confirm_yes_org_{o.get('id')}"):
                            if api_client.delete_organization(o.get('id')):
                                st.session_state[f"confirm_del_org_{o.get('id')}"] = False
                                st.success(f"Organization {o.get('id')} deleted")
                                st.experimental_rerun()
                    with c2:
                        if st.button("Cancel", key=f"confirm_no_org_{o.get('id')}"):
                            st.session_state[f"confirm_del_org_{o.get('id')}"] = False
                            st.rerun()
            
            # Inline edit
            if st.session_state.get(expand_key):
                st.markdown("---")
                st.write(f"**Editing Organization {o.get('id')}**")
                org_form_key = f"inline_edit_org_{o.get('id')}"
                with st.form(org_form_key):
                    new_name = st.text_input("Organization Name", value=o.get('name', ''))
                    type_opts = ["company", "division", "department", "team"]
                    current_type = o.get('org_unit_type', 'company').lower()
                    type_idx = type_opts.index(current_type) if current_type in type_opts else 0
                    new_type = st.selectbox("Organization Type", type_opts, index=type_idx, key=f"type_org_{o.get('id')}")
                    new_parent = st.number_input("Parent ID (0 for root)", min_value=0, value=o.get('parent_id') or 0, key=f"parent_org_{o.get('id')}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Save"):
                            update_data = {
                                "name": new_name,
                                "org_unit_type": new_type,
                                "parent_id": new_parent if new_parent > 0 else None
                            }
                            result = api_client.update_organization(o.get('id'), **update_data)
                            if result:
                                st.success(f"Organization {o.get('id')} updated!")
                                st.session_state[expand_key] = False
                                st.rerun()
                            else:
                                st.error("Failed to update organization")
                    with col2:
                        if st.form_submit_button("Cancel"):
                            st.session_state[expand_key] = False
                            st.rerun()
                st.markdown("---")

        st.divider()
        st.subheader("Organization Hierarchy")
        # Simple tree view
        for org in orgs:
            if org.get('parent_id') is None:
                st.write(f"📊 **{org.get('name')}** (Root)")
                for child_org in orgs:
                    if child_org.get('parent_id') == org.get('id'):
                        st.write(f"  └─ {child_org.get('name')} ({child_org.get('org_unit_type')})")
    else:
        st.info("No organizations found")

with tab2:
    st.subheader("Create New Organization")
    # load existing orgs for parent selection
    existing_orgs = api_client.get_organizations()
    org_map = {o.get('name'): o.get('id') for o in existing_orgs}

    with st.form("create_org_form"):
        name = st.text_input("Organization Name")
        org_unit_type = st.selectbox("Organization Type", ["company", "division", "department", "team"])

        parent_choice = "(root)"
        parent_names = [n for n in org_map.keys()]
        if parent_names:
            parent_choice = st.selectbox("Parent Organization", ["(root)"] + parent_names)
        selected_parent_id = None if parent_choice == "(root)" else org_map.get(parent_choice)

        description = st.text_area("Description (optional)")

        submitted = st.form_submit_button("Create Organization")

        if submitted:
            if not name:
                st.warning("Please enter an organization name")
            else:
                # require parent when creating a department
                if org_unit_type == 'department' and not selected_parent_id:
                    st.warning("When creating a department, please select its parent organization")
                else:
                    org_data = {
                        "name": name,
                        "org_unit_type": org_unit_type,
                        "description": description if description else None
                    }
                    if selected_parent_id:
                        org_data["parent_id"] = selected_parent_id

                    result = api_client.create_organization(**org_data)
                    if result:
                        st.success(f"Organization created successfully! ID: {result.get('id')}")
                    else:
                        st.error("Failed to create organization")

with tab3:
    st.subheader("Manage Existing Organization")
    
    # Get organization ID
    org_id = st.number_input("Organization ID", min_value=1)
    
    if st.button("Load Organization"):
        org = api_client.get_organization(org_id)
        if org:
            st.session_state.selected_org = org
        else:
            st.error("Organization not found")
    
    if "selected_org" in st.session_state:
        org = st.session_state.selected_org
        
        st.write("### Organization Details")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Name:** {org.get('name')}")
        with col2:
            st.write(f"**Type:** {org.get('org_unit_type', 'N/A')}")
        with col3:
            st.write(f"**Created:** {org.get('created_at', 'N/A')[:10]}")
        
        st.write(f"**Parent ID:** {org.get('parent_id', 'Root')}")
        st.write(f"**Updated:** {org.get('updated_at', 'N/A')[:10]}")
        
        st.divider()
        
        with st.form("update_org_form"):
            new_name = st.text_input("Organization Name", value=org.get('name', ''))
            current_type = org.get('org_unit_type', 'department').lower()
            type_index = 0
            if current_type in ["company", "division", "department", "team"]:
                type_index = ["company", "division", "department", "team"].index(current_type)
            new_type = st.selectbox("Organization Type", 
                                   ["company", "division", "department", "team"],
                                   index=type_index)
            new_parent_id = st.number_input("Parent Organization ID (0 for root)", min_value=0, 
                                           value=org.get('parent_id') or 0)
            new_description = st.text_area("Description", value=org.get('description', ''))
            
            col1, col2 = st.columns(2)
            with col1:
                update_clicked = st.form_submit_button("Update Organization")
                if update_clicked:
                    update_data = {
                        "name": new_name,
                        "org_unit_type": new_type,
                        "description": new_description if new_description else None
                    }
                    if new_parent_id > 0:
                        update_data["parent_id"] = new_parent_id
                    else:
                        update_data["parent_id"] = None
                    
                    result = api_client.update_organization(org_id, **update_data)
                    if result:
                        st.success("Organization updated successfully!")
                        if "selected_org" in st.session_state:
                            del st.session_state.selected_org
                        st.rerun()
                    else:
                        st.error("Failed to update organization")
            
            with col2:
                delete_clicked = st.form_submit_button("Delete Organization", type="secondary")
                if delete_clicked:
                    st.session_state['confirm_del_manage_org'] = True

    if st.session_state.get('confirm_del_manage_org', False):
        st.warning(f"⚠️ Confirm deletion of Organization {org_id} ({org.get('name')})? All departments, roles, and users will be deleted. This cannot be undone.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Yes, Delete All Permanently", key="confirm_del_org_manage_yes"):
                if api_client.delete_organization(org_id):
                    st.session_state['confirm_del_manage_org'] = False
                    st.success("Organization deleted successfully!")
                    if "selected_org" in st.session_state:
                        del st.session_state.selected_org
                    st.rerun()
        with c2:
            if st.button("Cancel", key="confirm_del_org_manage_no"):
                st.session_state['confirm_del_manage_org'] = False
                st.rerun()
