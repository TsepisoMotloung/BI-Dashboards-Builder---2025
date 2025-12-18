import requests
import streamlit as st
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any


def _read_api_url() -> str:
    # Load .env (allow reload)
    load_dotenv(override=True)
    return os.getenv("API_URL", "http://localhost:8000/api/v1")


class APIClient:
    def __init__(self, base_url: Optional[str] = None):
        # if base_url is None, read from environment now
        raw = base_url if base_url is not None else _read_api_url()
        self.base_url = raw.rstrip("/")
        self.token = None
        self.headers: Dict[str, str] = {}

    def reload_config(self):
        """Reload .env and update base URL dynamically at runtime."""
        self.base_url = _read_api_url().rstrip("/")
        return self.base_url

    def set_token(self, token: str):
        """Set the authentication token"""
        self.token = token
        # Keep headers minimal here; Content-Type may vary per request
        self.headers = {
            "Authorization": f"Bearer {token}"
        }

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[Any, Any]]:
        """Make HTTP request to API. Ensures headers merge and URL normalization."""
        try:
            # Normalize endpoint to start with '/'
            if not endpoint.startswith("/"):
                endpoint = f"/{endpoint}"
            url = f"{self.base_url}{endpoint}"

            # Merge headers: client headers (Authorization) + any per-call headers
            call_headers = kwargs.pop("headers", {}) or {}
            headers = self.headers.copy()
            headers.update(call_headers)
            
            # Ensure Authorization is set if we have a token
            if not headers.get('Authorization') and self.token:
                headers['Authorization'] = f"Bearer {self.token}"

            response = requests.request(method, url, headers=headers, timeout=10, **kwargs)
            response.raise_for_status()

            # Prefer JSON if available
            if response.status_code == 204 or not response.text:
                return None
            try:
                return response.json()
            except ValueError:
                return {"text": response.text}
        except requests.exceptions.RequestException as e:
            # Only show error if this isn't a normal 404 during cleanup
            error_msg = str(e)
            if "404" not in error_msg and "403" not in error_msg:
                st.error(f"API Error: {error_msg}")
            elif "403" in error_msg:
                st.error("Authorization failed. Please log in again.")
            return None

    def login(self, email: str, password: str) -> bool:
        """Login and get authentication token"""
        data = {"email": email, "password": password}
        response = self._make_request("POST", "/auth/login", json=data)
        if response and "access_token" in response:
            self.set_token(response["access_token"])
            return True
        return False

    # Users endpoints
    def get_users(self, skip: int = 0, limit: int = 100) -> list:
        """Get all users"""
        response = self._make_request("GET", f"/users/?skip={skip}&limit={limit}")
        return response if response else []

    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        return self._make_request("GET", f"/users/{user_id}")

    def create_user(self, email: str, password: str, full_name: str,
                    organization_id: int | None = None,
                    department_id: int | None = None,
                    role_id: int | None = None) -> Optional[Dict]:
        """Create new user with optional org/department/role associations"""
        data = {"email": email, "password": password, "full_name": full_name}
        if organization_id is not None:
            data["organization_id"] = organization_id
        if department_id is not None:
            data["department_id"] = department_id
        if role_id is not None:
            data["role_id"] = role_id
        return self._make_request("POST", "/users/", json=data)

    def update_user(self, user_id: int, **kwargs) -> Optional[Dict]:
        """Update user"""
        return self._make_request("PUT", f"/users/{user_id}", json=kwargs)

    def delete_user(self, user_id: int) -> bool:
        """Delete user"""
        try:
            response = requests.delete(
                f"{self.base_url}/users/{user_id}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            if "404" not in str(e):
                st.error(f"API Error: {str(e)}")
            return False

    # Roles endpoints
    def get_roles(self) -> list:
        """Get all roles"""
        response = self._make_request("GET", "/roles/")
        return response if response else []

    def get_role(self, role_id: int) -> Optional[Dict]:
        """Get role by ID"""
        return self._make_request("GET", f"/roles/{role_id}")

    def create_role(self, name: str, description: str = "") -> Optional[Dict]:
        """Create new role"""
        data = {"name": name, "description": description}
        return self._make_request("POST", "/roles/", json=data)
    def create_role(self, name: str, description: str = "", department_id: int | None = None) -> Optional[Dict]:
        """Create new role with optional department association"""
        data = {"name": name, "description": description}
        if department_id is not None:
            data["department_id"] = department_id
        return self._make_request("POST", "/roles/", json=data)

    def update_role(self, role_id: int, **kwargs) -> Optional[Dict]:
        """Update role"""
        return self._make_request("PUT", f"/roles/{role_id}", json=kwargs)

    def delete_role(self, role_id: int) -> bool:
        """Delete role"""
        try:
            response = requests.delete(
                f"{self.base_url}/roles/{role_id}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            if "404" not in str(e):
                st.error(f"API Error: {str(e)}")
            return False

    # Uploads endpoints
    def get_uploads(self, skip: int = 0, limit: int = 100) -> list:
        """Get all uploads"""
        response = self._make_request("GET", f"/uploads/?skip={skip}&limit={limit}")
        return response if response else []

    def list_tables(self) -> list:
        """List all existing dynamic tables available for appending."""
        response = self._make_request("GET", "/uploads/tables/list")
        if response and isinstance(response, dict) and 'tables' in response:
            return response['tables']
        return []

    def get_upload(self, upload_id: int) -> Optional[Dict]:
        """Get upload by ID"""
        return self._make_request("GET", f"/uploads/{upload_id}")

    def upload_file(self, file_path: str, upload_request: dict) -> Optional[Dict]:
        """Upload a file with upload_request options.

        `upload_request` is a dict matching the backend `UploadRequest` model
        (e.g. target_table_name, mode, add_missing_columns, validate_only, column_type_overrides, etc.)
        """
        import json
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.split('/')[-1], f)}
            data = {"upload_request": json.dumps(upload_request)}

            # Ensure headers are set properly with auth
            headers = self.headers.copy() if self.headers else {}
            if not headers.get('Authorization') and self.token:
                headers['Authorization'] = f"Bearer {self.token}"

            try:
                url = f"{self.base_url}/uploads/"
                response = requests.post(
                    url,
                    files=files,
                    data=data,
                    headers=headers,
                    timeout=120
                )
                response.raise_for_status()
                try:
                    return response.json()
                except ValueError:
                    return {"text": response.text}
            except requests.exceptions.RequestException as e:
                error_msg = str(e)
                if "403" in error_msg:
                    st.error(f"Upload Error: Authentication failed. Please log in again.")
                else:
                    st.error(f"Upload Error: {error_msg}")
                return None

    def preview_file(self, file_path: str) -> Optional[Dict]:
        """Send a file to `/uploads/preview` and return detected headers/sample types."""
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.split('/')[-1], f)}
            # Ensure headers are set properly
            headers = self.headers.copy() if self.headers else {}
            if not headers.get('Authorization') and self.token:
                headers['Authorization'] = f"Bearer {self.token}"
            try:
                url = f"{self.base_url}/uploads/preview"
                response = requests.post(url, files=files, headers=headers, timeout=30)
                response.raise_for_status()
                try:
                    return response.json()
                except ValueError:
                    return {"text": response.text}
            except requests.exceptions.RequestException as e:
                error_msg = str(e)
                if "403" in error_msg:
                    st.error(f"Preview Error: Authentication failed. Please log in again.")
                else:
                    st.error(f"Preview Error: {error_msg}")
                return None

    def get_upload_logs(self, upload_id: int) -> Optional[Dict]:
        """Get logs for an upload"""
        response = self._make_request("GET", f"/uploads/{upload_id}/logs")
        return response if response else []
    def get_data_models(self, skip: int = 0, limit: int = 100) -> list:
        """Get all data models"""
        response = self._make_request("GET", f"/data-models/?skip={skip}&limit={limit}")
        return response if response else []

    def get_data_model(self, model_id: int) -> Optional[Dict]:
        """Get data model by ID"""
        return self._make_request("GET", f"/data-models/{model_id}")

    def create_data_model(self, name: str, fields: list, description: str = None, **kwargs) -> Optional[Dict]:
        """Create new data model with schema_definition"""
        data = {
            "name": name,
            "schema_definition": {
                "fields": fields,
                "primary_key": "id",
                "indexes": []
            }
        }
        if description:
            data["description"] = description
        return self._make_request("POST", "/data-models/", json=data)

    def update_data_model(self, model_id: int, fields: list = None, description: str = None, **kwargs) -> Optional[Dict]:
        """Update data model"""
        data = {}
        if fields:
            data["schema_definition"] = {
                "fields": fields,
                "primary_key": "id",
                "indexes": []
            }
        if description is not None:
            data["description"] = description
        return self._make_request("PUT", f"/data-models/{model_id}", json=data)

    def delete_data_model(self, model_id: int) -> bool:
        """Delete data model"""
        try:
            response = requests.delete(
                f"{self.base_url}/data-models/{model_id}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            if "404" not in str(e):
                st.error(f"API Error: {str(e)}")
            return False

    # Organization endpoints
    def get_organizations(self) -> list:
        """Get all organizations"""
        response = self._make_request("GET", "/organizations/")
        return response if response else []

    def get_organization(self, org_id: int) -> Optional[Dict]:
        """Get organization by ID"""
        return self._make_request("GET", f"/organizations/{org_id}")

    def create_organization(self, **kwargs) -> Optional[Dict]:
        """Create new organization"""
        return self._make_request("POST", "/organizations/", json=kwargs)

    def update_organization(self, org_id: int, **kwargs) -> Optional[Dict]:
        """Update organization"""
        return self._make_request("PUT", f"/organizations/{org_id}", json=kwargs)

    def delete_organization(self, org_id: int) -> bool:
        """Delete organization"""
        try:
            response = requests.delete(
                f"{self.base_url}/organizations/{org_id}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            if "404" not in str(e):
                st.error(f"API Error: {str(e)}")
            return False

    # Departments endpoints
    def get_departments(self) -> list:
        """Get all departments"""
        response = self._make_request("GET", "/departments/")
        return response if response else []

    def get_department(self, dep_id: int) -> Optional[Dict]:
        """Get department by ID"""
        return self._make_request("GET", f"/departments/{dep_id}")

    def create_department(self, name: str, parent_id: int) -> Optional[Dict]:
        """Create new department (requires parent org)"""
        data = {"name": name, "organization_id": parent_id}
        return self._make_request("POST", "/departments/", json=data)

    def update_department(self, dep_id: int, **kwargs) -> Optional[Dict]:
        """Update department"""
        return self._make_request("PUT", f"/departments/{dep_id}", json=kwargs)

    def delete_department(self, dep_id: int) -> bool:
        """Delete department"""
        try:
            response = requests.delete(
                f"{self.base_url}/departments/{dep_id}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            if "404" not in str(e):
                st.error(f"API Error: {str(e)}")
            return False


# Create a global API client instance
api_client = APIClient()
