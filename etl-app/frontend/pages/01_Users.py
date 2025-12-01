import streamlit as st
import sys
sys.path.append('..')
from api_client import api_client

st.set_page_config(page_title="User Management", page_icon="👥", layout="wide")

# Check authentication
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.error("Please log in from the main page")
    st.stop()

st.header("👥 User Management")

# Initialize API client with token
if st.session_state.token:
    api_client.set_token(st.session_state.token)

tab1, tab2, tab3 = st.tabs(["View Users", "Create User", "Manage User"])

with tab1:
    st.subheader("All Users")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        skip = st.number_input("Skip", min_value=0, value=0)
    with col2:
        limit = st.number_input("Limit", min_value=1, value=100)
    
    users = api_client.get_users(skip=skip, limit=limit)
    
    if users:
        st.write(f"Showing {len(users)} users (skip={skip} limit={limit})")

        # Header row for actions table
        st.markdown("""
        <style>
        .small-col { width: 120px; display: inline-block }
        </style>
        """, unsafe_allow_html=True)

        # Render rows with inline action buttons for convenience
        for u in users:
            # Initialize expand state for this user
            expand_key = f"expand_user_{u.get('id')}"
            if expand_key not in st.session_state:
                st.session_state[expand_key] = False
            
            # Header row
            cols = st.columns([1, 3, 3, 2, 2, 2])
            with cols[0]:
                st.write(u.get('id'))
            with cols[1]:
                st.write(u.get('email'))
            with cols[2]:
                st.write(u.get('full_name'))
            with cols[3]:
                # show primary role and primary org unit
                roles = u.get('roles', [])
                primary_role = roles[0] if roles else 'N/A'
                ous = u.get('organizational_units', [])
                primary_ou = 'N/A'
                if ous:
                    # prefer department if available
                    dept = next((x for x in ous if x.get('type') == 'department'), None)
                    primary_ou = dept.get('name') if dept else ous[0].get('name')
                st.write(f"{primary_role} / {primary_ou}")
            with cols[4]:
                created = u.get('created_at')
                st.write(created[:10] if created else 'N/A')
            with cols[5]:
                col_buttons = st.columns(2)
                with col_buttons[0]:
                    if st.button("Edit", key=f"edit_user_{u.get('id')}"):
                        st.session_state[expand_key] = not st.session_state[expand_key]
                with col_buttons[1]:
                    if st.button("Del", key=f"del_user_{u.get('id')}"):
                        st.session_state[f"confirm_del_user_{u.get('id')}"] = True
                if st.session_state.get(f"confirm_del_user_{u.get('id')}", False):
                    st.warning(f"⚠️ Confirm deletion of User {u.get('id')} ({u.get('email')})? This cannot be undone.")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Yes, Delete", key=f"confirm_yes_user_{u.get('id')}"):
                            if api_client.delete_user(u.get('id')):
                                st.session_state[f"confirm_del_user_{u.get('id')}"] = False
                                st.success(f"User {u.get('id')} deleted")
                                st.experimental_rerun()
                    with c2:
                        if st.button("Cancel", key=f"confirm_no_user_{u.get('id')}"):
                            st.session_state[f"confirm_del_user_{u.get('id')}"] = False
                            st.rerun()
            
            # Inline edit form
            if st.session_state.get(expand_key):
                with st.container():
                    st.markdown("---")
                    st.write(f"**Editing User {u.get('id')}**")
                    with st.form(f"inline_edit_user_{u.get('id')}"):
                        new_name = st.text_input("Full Name", value=u.get('full_name', ''))
                        status_opts = ["pending", "active", "suspended", "inactive"]
                        status_idx = status_opts.index(u.get('status', 'active')) if u.get('status') in status_opts else 1
                        new_status = st.selectbox("Status", status_opts, index=status_idx, key=f"status_user_{u.get('id')}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Save"):
                                result = api_client.update_user(u.get('id'), full_name=new_name, status=new_status)
                                if result:
                                    st.success(f"User {u.get('id')} updated!")
                                    st.session_state[expand_key] = False
                                    st.experimental_rerun()
                                else:
                                    st.error("Failed to update user")
                        with col2:
                            if st.form_submit_button("Cancel"):
                                st.session_state[expand_key] = False
                                st.experimental_rerun()
                    st.markdown("---")
    else:
        st.info("No users found")

with tab2:
    st.subheader("Create New User")
    
    # load organizations, departments and roles for dropdowns
    orgs = api_client.get_organizations()
    depts = api_client.get_departments()
    roles = api_client.get_roles()

    # build maps name -> id
    org_map = {o.get('name'): o.get('id') for o in orgs}
    dept_map = {d.get('name'): d.get('id') for d in depts}
    company_names = list(org_map.keys())
    role_map = {r.get('name'): r.get('id') for r in roles}

    with st.form("create_user_form"):
        email = st.text_input("Email")
        full_name = st.text_input("Full Name")
        password = st.text_input("Password", type="password")

        # Organization dropdown
        org_choice = None
        if company_names:
            org_choice = st.selectbox("Organization", ["(select)"] + company_names)
            selected_org_id = None if org_choice == "(select)" else org_map.get(org_choice)
        else:
            selected_org_id = None

        # Department dropdown (filtered by selected organization)
        dept_names = [d.get('name') for d in depts]
        if selected_org_id:
            filtered = [d for d in depts if d.get('organization_id') == selected_org_id]
            if filtered:
                dept_names = [d.get('name') for d in filtered]

        dept_choice = st.selectbox("Department", ["(select)"] + dept_names) if dept_names else st.selectbox("Department", ["(select)"])
        selected_dept_id = None if dept_choice == "(select)" else dept_map.get(dept_choice)

        # Role dropdown (filtered by selected department when possible)
        role_names = [r.get('name') for r in roles]
        if selected_dept_id:
            filtered_roles = [r for r in roles if r.get('department_id') == selected_dept_id]
            if filtered_roles:
                role_names = [r.get('name') for r in filtered_roles]

        role_choice = st.selectbox("Role", ["(select)"] + role_names) if role_names else st.selectbox("Role", ["(select)"])
        selected_role_id = None if role_choice == "(select)" else role_map.get(role_choice)

        submitted = st.form_submit_button("Create User")

        if submitted:
            # require email/name/password and selections for org/dept/role
            missing = []
            if not email:
                missing.append("Email")
            if not full_name:
                missing.append("Full Name")
            if not password:
                missing.append("Password")
            if not selected_org_id:
                missing.append("Organization")
            if not selected_dept_id:
                missing.append("Department")
            if not selected_role_id:
                missing.append("Role")

            if missing:
                st.warning("Please provide: " + ", ".join(missing))
            else:
                result = api_client.create_user(
                    email=email,
                    password=password,
                    full_name=full_name,
                    organization_id=selected_org_id,
                    department_id=selected_dept_id,
                    role_id=selected_role_id
                )
                if result:
                    st.success(f"User created successfully! ID: {result.get('id')}")
                else:
                    st.error("Failed to create user")

# Manage user rendering logic (re-usable)

def render_manage_user(user, context: str = ""):
    st.write("### User Details")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Email:** {user.get('email')}")
        st.write(f"**Name:** {user.get('full_name')}")
        # show roles and organization path
        st.write("**Roles:** " + ", ".join(user.get('roles', [])))
        ous = user.get('organizational_units', [])
        if ous:
            st.write("**Org Units:**")
            for ou in ous:
                st.write(f"- {ou.get('name')} ({ou.get('type')})")
    with col2:
        st.write(f"**Status:** {user.get('status')}")
        st.write(f"**Created:** {user.get('created_at', 'N/A')[:10]}")
    
    st.divider()

    suffix = f"_{context}" if context else ''
    form_key = f"update_user_form_{user.get('id')}{suffix}"
    with st.form(form_key):
        new_status = st.selectbox("Update Status", ["pending", "active", "suspended", "inactive"], 
                                 index=["pending", "active", "suspended", "inactive"].index(user.get('status', 'active')))
        new_name = st.text_input("Full Name", value=user.get('full_name', ''))
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Update User"):
                result = api_client.update_user(user.get('id'), full_name=new_name, status=new_status)
                if result:
                    st.success("User updated successfully!")
                    if 'selected_user' in st.session_state:
                        del st.session_state.selected_user
                    st.experimental_rerun()
                else:
                    st.error("Failed to update user")
        
        with col2:
            if st.form_submit_button("Delete User", type="secondary"):
                st.session_state[f'confirm_del_manage_user_{user.get("id")}'] = True

    confirm_key = f'confirm_del_manage_user_{user.get("id")}'
    if st.session_state.get(confirm_key, False):
        st.warning(f"⚠️ Confirm deletion of User {user.get('id')} ({user.get('email')})? This cannot be undone.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Yes, Delete Permanently", key=f"confirm_del_user_manage_yes_{user.get('id')}"):
                if api_client.delete_user(user.get('id')):
                    st.session_state[confirm_key] = False
                    st.success("User deleted successfully!")
                    if 'selected_user' in st.session_state:
                        del st.session_state.selected_user
                    st.experimental_rerun()
        with c2:
            if st.button("Cancel", key=f"confirm_del_user_manage_no_{user.get('id')}"):
                st.session_state[confirm_key] = False
                st.rerun()


with tab3:
    st.subheader("Manage Existing User")
    
    # Get user ID
    user_id = st.number_input("User ID", min_value=1)
    
    if st.button("Load User"):
        user = api_client.get_user(user_id)
        if user:
            st.session_state.selected_user = user

    if "selected_user" in st.session_state:
        user = st.session_state.selected_user
        render_manage_user(user, context="tab")

# If user was loaded from the table, also render Manage section immediately below tabs for convenience
if 'selected_user' in st.session_state and st.session_state.get('selected_user'):
    st.markdown("---")
    st.header("Loaded Selection")
    render_manage_user(st.session_state.get('selected_user'), context="loaded")
