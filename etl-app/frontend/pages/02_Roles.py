import streamlit as st
import sys
sys.path.append('..')
from api_client import api_client

st.set_page_config(page_title="Role Management", page_icon="👨‍💼", layout="wide")

# Check authentication
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.error("Please log in from the main page")
    st.stop()

st.header("👨‍💼 Role Management")

# Initialize API client with token
if st.session_state.token:
    api_client.set_token(st.session_state.token)

tab1, tab2, tab3 = st.tabs(["View Roles", "Create Role", "Manage Role"])

with tab1:
    st.subheader("All Roles")
    
    roles = api_client.get_roles()
    
    if roles:
        st.write(f"Showing {len(roles)} roles")
        for r in roles:
            expand_key = f"expand_role_{r.get('id')}"
            if expand_key not in st.session_state:
                st.session_state[expand_key] = False
            
            cols = st.columns([1, 3, 4, 2, 1.5])
            with cols[0]:
                st.write(f"ID: {r.get('id')}")

            with cols[1]:
                st.write(f"{r.get('name')}")

            with cols[2]:
                org_name = r.get('organization_name') or 'N/A'
                st.write(f"Org: {org_name}")
                
            with cols[3]:
                st.write(f"Department: {r.get('department_name')}")
            
            with cols[4]:
                col_buttons = st.columns(2)
                with col_buttons[0]:
                    if st.button("Edit", key=f"edit_role_{r.get('id')}"):
                        st.session_state[expand_key] = not st.session_state[expand_key]
                with col_buttons[1]:
                    if st.button("Del", key=f"del_role_{r.get('id')}"):
                        st.session_state[f"confirm_del_role_{r.get('id')}"] = True
                if st.session_state.get(f"confirm_del_role_{r.get('id')}", False):
                    st.warning(f"⚠️ Confirm deletion of Role {r.get('id')} ({r.get('name')})? This cannot be undone.")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Yes, Delete", key=f"confirm_yes_role_{r.get('id')}"):
                            if api_client.delete_role(r.get('id')):
                                st.session_state[f"confirm_del_role_{r.get('id')}"] = False
                                st.success(f"Role {r.get('id')} deleted")
                                st.experimental_rerun()
                    with c2:
                        if st.button("Cancel", key=f"confirm_no_role_{r.get('id')}"):
                            st.session_state[f"confirm_del_role_{r.get('id')}"] = False
                            st.rerun()
            
            # Inline edit
            if st.session_state.get(expand_key):
                st.markdown("---")
                st.write(f"**Editing Role {r.get('id')}**")
                with st.form(f"inline_edit_role_{r.get('id')}"):
                    new_name = st.text_input("Role Name", value=r.get('name', ''))
                    new_desc = st.text_area("Description", value=r.get('description', ''))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Save"):
                            result = api_client.update_role(r.get('id'), name=new_name, description=new_desc)
                            if result:
                                st.success(f"Role {r.get('id')} updated!")
                                st.session_state[expand_key] = False
                                st.experimental_rerun()
                            else:
                                st.error("Failed to update role")
                    with col2:
                        if st.form_submit_button("Cancel"):
                            st.session_state[expand_key] = False
                            st.experimental_rerun()
                st.markdown("---")
    else:
        st.info("No roles found")

with tab2:
    st.subheader("Create New Role")
    # load organizations and departments for dropdowns
    orgs = api_client.get_organizations()
    depts = api_client.get_departments()
    dept_map = {d.get('name'): d.get('id') for d in depts}
    org_map = {o.get('name'): o.get('id') for o in orgs}

    with st.form("create_role_form"):
        name = st.text_input("Role Name")
        description = st.text_area("Description")

        # Organization dropdown
        org_names = list(org_map.keys())
        org_choice = st.selectbox("Organization", ["(none)"] + org_names) if org_names else st.selectbox("Organization", ["(none)"])
        selected_org_id = None if org_choice == "(none)" else org_map.get(org_choice)

        # Department dropdown filtered by selected org
        dept_names = [d.get('name') for d in depts]
        if selected_org_id:
            filtered = [d for d in depts if d.get('organization_id') == selected_org_id]
            if filtered:
                dept_names = [d.get('name') for d in filtered]

        dept_choice = st.selectbox("Department", ["(none)"] + dept_names) if dept_names else st.selectbox("Department", ["(none)"])
        selected_dept_id = None if dept_choice == "(none)" else dept_map.get(dept_choice)

        submitted = st.form_submit_button("Create Role")

        if submitted:
            missing = []
            if not name:
                missing.append("Role Name")
            if not selected_org_id:
                missing.append("Organization")
            if not selected_dept_id:
                missing.append("Department")

            if missing:
                st.warning("Please provide: " + ", ".join(missing))
            else:
                result = api_client.create_role(name=name, description=description, department_id=selected_dept_id)
                if result:
                    st.success(f"Role created successfully! ID: {result.get('id')}")
                else:
                    st.error("Failed to create role")


# Manage role rendering

def render_manage_role(role, context: str = ""):
    st.write("### Role Details")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Name:** {role.get('name')}")
        st.write(f"**Description:** {role.get('description', 'N/A')}")
    with col2:
        st.write(f"**Created:** {role.get('created_at', 'N/A')[:10]}")
        st.write(f"**System Role:** {role.get('is_system_role', False)}")
    st.divider()
    suffix = f"_{context}" if context else ''
    form_key = f"update_role_form_{role.get('id')}{suffix}"
    with st.form(form_key):
        new_name = st.text_input("Role Name", value=role.get('name', ''))
        new_description = st.text_area("Description", value=role.get('description', ''))

        # Organization and Department selectors (same as create form)
        orgs = api_client.get_organizations()
        depts = api_client.get_departments()
        org_map = {o.get('name'): o.get('id') for o in orgs}
        dept_map = {d.get('name'): d.get('id') for d in depts}

        # determine current selection from role data
        current_dept_id = role.get('department_id')
        current_org_id = None
        if current_dept_id:
            cur_dept = next((d for d in depts if d.get('id') == current_dept_id), None)
            if cur_dept:
                current_org_id = cur_dept.get('organization_id')

        org_names = list(org_map.keys())
        org_choice = None
        if org_names:
            # preselect current org if available
            default_index = 0
            if current_org_id:
                try:
                    default_name = next(k for k, v in org_map.items() if v == current_org_id)
                    default_index = org_names.index(default_name) + 1
                except StopIteration:
                    default_index = 0
            org_choice = st.selectbox("Organization", ["(none)"] + org_names, index=default_index)
            selected_org_id = None if org_choice == "(none)" else org_map.get(org_choice)
        else:
            selected_org_id = None

        dept_names = [d.get('name') for d in depts]
        if selected_org_id:
            filtered = [d for d in depts if d.get('organization_id') == selected_org_id]
            if filtered:
                dept_names = [d.get('name') for d in filtered]

        # preselect dept if possible
        default_dept_index = 0
        if current_dept_id:
            try:
                default_dept_name = next(d.get('name') for d in depts if d.get('id') == current_dept_id)
                default_dept_index = dept_names.index(default_dept_name) + 1
            except StopIteration:
                default_dept_index = 0

        dept_choice = st.selectbox("Department", ["(none)"] + dept_names, index=default_dept_index) if dept_names else st.selectbox("Department", ["(none)"])
        selected_dept_id = None if dept_choice == "(none)" else dept_map.get(dept_choice)

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Update Role"):
                # include department_id in update payload
                payload = {"name": new_name, "description": new_description}
                if selected_dept_id is not None:
                    payload["department_id"] = selected_dept_id
                result = api_client.update_role(role.get('id'), **payload)
                if result:
                    st.success("Role updated successfully!")
                    if 'selected_role' in st.session_state:
                        del st.session_state['selected_role']
                    st.experimental_rerun()
                else:
                    st.error("Failed to update role")
        with col2:
            if st.form_submit_button("Delete Role", type="secondary"):
                st.session_state[f'confirm_del_manage_role_{role.get("id")}'] = True

    confirm_key = f'confirm_del_manage_role_{role.get("id")}'
    if st.session_state.get(confirm_key, False):
        st.warning(f"⚠️ Confirm deletion of Role {role.get('id')} ({role.get('name')})? This cannot be undone.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Yes, Delete Permanently", key=f"confirm_del_role_manage_yes_{role.get('id')}"):
                if api_client.delete_role(role.get('id')):
                    st.session_state[confirm_key] = False
                    st.success("Role deleted successfully!")
                    if 'selected_role' in st.session_state:
                        del st.session_state['selected_role']
                    st.experimental_rerun()
        with c2:
            if st.button("Cancel", key=f"confirm_del_role_manage_no_{role.get('id')}"):
                st.session_state[confirm_key] = False
                st.rerun()


with tab3:
    st.subheader("Manage Existing Role")
    
    # Get role ID
    role_id = st.number_input("Role ID", min_value=1)
    
    if st.button("Load Role"):
        role = api_client.get_role(role_id)
        if role:
            st.session_state.selected_role = role
        else:
            st.error("Role not found")
    
    if "selected_role" in st.session_state:
        role = st.session_state.selected_role
        render_manage_role(role, context="tab")

# If role loaded from table, render manage view below tabs
if 'selected_role' in st.session_state and st.session_state.get('selected_role'):
    st.markdown('---')
    st.header('Loaded Role')
    render_manage_role(st.session_state.get('selected_role'), context="loaded")
