import streamlit as st
import sys
sys.path.append('..')
from api_client import api_client

st.set_page_config(page_title="Departments", page_icon="🏬", layout="wide")

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.error("Please log in from the main page")
    st.stop()

st.header("🏬 Department Management")

if st.session_state.token:
    api_client.set_token(st.session_state.token)

tab1, tab2, tab3 = st.tabs(["View Departments", "Create Department", "Manage Department"]) 

with tab1:
    st.subheader("All Departments")
    deps = api_client.get_departments()
    if deps:
        st.write(f"Showing {len(deps)} departments")
        orgs = api_client.get_organizations()
        org_map_id = {o.get('id'): o.get('name') for o in orgs}
        for d in deps:
            cols = st.columns([1, 4, 3, 2, 2])
            with cols[0]:
                st.write(d.get('id'))
            with cols[1]:
                st.write(d.get('name'))
            with cols[2]:
                org_name = org_map_id.get(d.get('organization_id')) if d.get('organization_id') else None
                st.write(org_name or 'N/A')
            with cols[3]:
                created = d.get('created_at')
                st.write(created[:10] if created else 'N/A')
            with cols[4]:
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Edit", key=f"edit_dep_{d.get('id')}"):
                        st.session_state[f"selected_dep"] = d
                with c2:
                    if st.button("Del", key=f"del_dep_{d.get('id')}"):
                        st.session_state[f"confirm_del_dep_{d.get('id')}"] = True
                if st.session_state.get(f"confirm_del_dep_{d.get('id')}", False):
                    st.warning(f"⚠️ Confirm deletion of Department {d.get('id')} ({d.get('name')})? All roles and users will be deleted. This cannot be undone.")
                    c1, c2_conf = st.columns(2)
                    with c1:
                        if st.button("Yes, Delete All", key=f"confirm_yes_dep_{d.get('id')}"):
                            if api_client.delete_department(d.get('id')):
                                st.session_state[f"confirm_del_dep_{d.get('id')}"] = False
                                st.success(f"Department {d.get('id')} deleted")
                                st.experimental_rerun()
                    with c2_conf:
                        if st.button("Cancel", key=f"confirm_no_dep_{d.get('id')}"):
                            st.session_state[f"confirm_del_dep_{d.get('id')}"] = False
                            st.rerun()
    else:
        st.info("No departments found")

with tab2:
    st.subheader("Create New Department")
    orgs = api_client.get_organizations()
    org_map = {o.get('name'): o.get('id') for o in orgs}
    parent_names = list(org_map.keys())
    with st.form("create_dep_form"):
        name = st.text_input("Department Name")
        parent_choice = st.selectbox("Parent Organization", ["(select)"] + parent_names) if parent_names else st.selectbox("Parent Organization", ["(select)"])
        parent_id = None if parent_choice == '(select)' else org_map.get(parent_choice)
        submitted = st.form_submit_button("Create Department")
        if submitted:
            if not name:
                st.warning("Please enter department name")
            elif not parent_id:
                st.warning("Please select parent organization for department")
            else:
                # api_client.create_department maps parent_id -> organization_id
                result = api_client.create_department(name=name, parent_id=parent_id)
                if result:
                    st.success(f"Department created successfully! ID: {result.get('id')}")
                else:
                    st.error("Failed to create department")

with tab3:
    st.subheader("Manage Department")
    dep_id = st.number_input("Department ID", min_value=1)
    if st.button("Load Department"):
        d = api_client.get_department(dep_id)
        if d:
            st.session_state.selected_dep = d
        else:
            st.error("Department not found")

    if 'selected_dep' in st.session_state:
        d = st.session_state.selected_dep
        st.write(f"### Department {d.get('id')}")
        with st.form("update_dep_form"):
            new_name = st.text_input("Department Name", value=d.get('name'))
            orgs = api_client.get_organizations()
            org_map = {o.get('name'): o.get('id') for o in orgs}
            parent_choice = st.selectbox("Parent Organization", ["(root)"] + list(org_map.keys()), index=0)
            new_parent_id = None if parent_choice == '(root)' else org_map.get(parent_choice)
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Update Department"):
                    # backend expects `organization_id` for department parent
                    payload = {"name": new_name, "organization_id": new_parent_id}
                    result = api_client.update_department(d.get('id'), **payload)
                    if result:
                        st.success("Department updated")
                        del st.session_state.selected_dep
                        st.experimental_rerun()
                    else:
                        st.error("Failed to update department")
            with col2:
                if st.form_submit_button("Delete Department", type="secondary"):
                    st.session_state['confirm_del_manage_dep'] = True

    if st.session_state.get('confirm_del_manage_dep', False):
        st.warning(f"⚠️ Confirm deletion of Department {d.get('id')} ({d.get('name')})? All roles and users will be deleted. This cannot be undone.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Yes, Delete All Permanently", key="confirm_del_dep_manage_yes"):
                if api_client.delete_department(d.get('id')):
                    st.session_state['confirm_del_manage_dep'] = False
                    st.success("Department deleted")
                    if 'selected_dep' in st.session_state:
                        del st.session_state.selected_dep
                    st.experimental_rerun()
        with c2:
            if st.button("Cancel", key="confirm_del_dep_manage_no"):
                st.session_state['confirm_del_manage_dep'] = False
                st.rerun()
