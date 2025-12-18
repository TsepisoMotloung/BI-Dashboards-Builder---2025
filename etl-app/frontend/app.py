import streamlit as st
from api_client import api_client
from config import ADMIN_EMAIL, ADMIN_PASSWORD

# Page configuration
st.set_page_config(
    page_title="ETL Upload Manager",
    page_icon="📤",
    layout="wide"
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "token" not in st.session_state:
    st.session_state.token = None

def login_user():
    """Handle user login"""
    st.subheader("🔐 Login")
    email = st.text_input("Email", value=ADMIN_EMAIL)
    password = st.text_input("Password", type="password", value=ADMIN_PASSWORD)
    
    if st.button("Login", type="primary"):
        if api_client.login(email, password):
            st.session_state.authenticated = True
            st.session_state.token = api_client.token
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Invalid credentials")

def logout_user():
    """Handle user logout"""
    st.session_state.authenticated = False
    st.session_state.token = None
    st.success("Logged out successfully!")
    st.rerun()

def main():
    """Main application"""
    
    # Reload config at runtime
    try:
        api_client.reload_config()
    except Exception:
        pass

    # Header
    st.title("📤 ETL Upload Manager")
    
    # Sidebar
    with st.sidebar:
        st.title("Menu")
        
        if st.session_state.authenticated:
            st.write(f"**Logged in as:** {ADMIN_EMAIL}")
            if st.button("🚪 Logout", use_container_width=True):
                logout_user()
        else:
            st.write("Please log in to continue.")
    
    # Main content
    if not st.session_state.authenticated:
        login_user()
    else:
        st.write("Navigate to **Upload Data Files** in the sidebar to upload and manage data.")

if __name__ == "__main__":
    main()

