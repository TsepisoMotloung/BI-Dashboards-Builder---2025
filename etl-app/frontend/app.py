import streamlit as st
from api_client import api_client
from config import ADMIN_EMAIL, ADMIN_PASSWORD
import datetime

# Page configuration
st.set_page_config(
    page_title="ETL Admin Dashboard",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.85rem;
        font-weight: bold;
    }
    .status-active {
        background-color: #d4edda;
        color: #155724;
    }
    .status-pending {
        background-color: #fff3cd;
        color: #856404;
    }
    .status-failed {
        background-color: #f8d7da;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "token" not in st.session_state:
    st.session_state.token = None

def login_user():
    """Handle user login"""
    st.subheader("Admin Login")
    email = st.text_input("Email", value=ADMIN_EMAIL)
    password = st.text_input("Password", type="password", value=ADMIN_PASSWORD)
    
    if st.button("Login"):
        if api_client.login(email, password):
            st.session_state.authenticated = True
            st.session_state.token = api_client.token
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid credentials")

def logout_user():
    """Handle user logout"""
    st.session_state.authenticated = False
    st.session_state.token = None
    st.success("Logged out successfully!")
    st.rerun()

def main():
    """Main application"""
    
    # Ensure api_client reads any updated API_URL from .env
    try:
        api_client.reload_config()
    except Exception:
        pass

    # Header
    st.markdown('<div class="main-header">⚙️ ETL Admin Dashboard</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("Navigation")
        
        if st.session_state.authenticated:
            st.write(f"**Logged in as:** {ADMIN_EMAIL}")
            if st.button("Logout", key="logout"):
                logout_user()
            
            st.divider()
            st.subheader("Admin Functions")
            
            # Display the current time
            st.write(f"**Current Time:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.write("Please log in to access the admin dashboard.")
    
    # Main content
    if not st.session_state.authenticated:
        login_user()
    else:
        # Create tabs for different admin functions
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["Users", "Roles", "Uploads", "Data Models", "Organization"]
        )
        
        with tab1:
            st.subheader("User Management")
            st.write("Manage users, roles, and permissions")
            
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("➕ Add User"):
                    st.session_state.show_add_user = True
            
            users = api_client.get_users()
            if users:
                st.dataframe(users, use_container_width=True)
            else:
                st.info("No users found")
        
        with tab2:
            st.subheader("Role Management")
            st.write("Manage roles and permissions")
            
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("➕ Add Role"):
                    st.session_state.show_add_role = True
            
            roles = api_client.get_roles()
            if roles:
                st.dataframe(roles, use_container_width=True)
            else:
                st.info("No roles found")
        
        with tab3:
            st.subheader("Upload Management")
            st.write("View and manage data uploads")
            
            uploads = api_client.get_uploads()
            if uploads:
                for upload in uploads:
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.write(f"**File:** {upload.get('file_name', 'N/A')}")
                        with col2:
                            status = upload.get('status', 'pending')
                            status_class = f"status-{status.lower()}"
                            st.markdown(f'<span class="status-badge {status_class}">{status}</span>', unsafe_allow_html=True)
                        with col3:
                            st.write(f"**Created:** {upload.get('created_at', 'N/A')[:10]}")
            else:
                st.info("No uploads found")
        
        with tab4:
            st.subheader("Data Model Management")
            st.write("Create and manage data models")
            
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("➕ Add Data Model"):
                    st.session_state.show_add_model = True
            
            models = api_client.get_data_models()
            if models:
                st.dataframe(models, use_container_width=True)
            else:
                st.info("No data models found")
        
        with tab5:
            st.subheader("Organization Management")
            st.write("Manage organization units and hierarchy")
            
            orgs = api_client.get_organizations()
            if orgs:
                st.dataframe(orgs, use_container_width=True)
            else:
                st.info("No organizations found")

if __name__ == "__main__":
    main()
