# ETL Admin Dashboard

A Streamlit-based admin dashboard for managing the ETL application. This provides a user-friendly interface to manage users, roles, uploads, data models, and organization units.

## Features

- 👥 **User Management** - Create, view, and manage users
- 👨‍💼 **Role Management** - Create and manage roles and permissions
- 📤 **Upload Management** - View uploads, monitor status, and manage files
- 📊 **Data Model Management** - Create and manage data models with custom fields
- 🏢 **Organization Management** - View and manage organization units and hierarchy

## Installation

### Prerequisites
- Python 3.8+
- ETL API running on `http://localhost:8000/api/v1`

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```bash
API_URL=http://localhost:8000/api/v1
API_KEY=your-api-key
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=password123
```

## Running the Dashboard

Start the Streamlit app:
```bash
streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`

## Structure

```
frontend/
├── app.py              # Main dashboard application
├── api_client.py       # API client for backend communication
├── config.py           # Configuration management
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
├── README.md          # This file
└── pages/
    ├── 01_Users.py           # User management page
    ├── 02_Roles.py           # Role management page
    ├── 03_Uploads.py         # Upload management page
    ├── 04_Data_Models.py     # Data model management page
    └── 05_Organization.py    # Organization management page
```

## Default Credentials

- **Email:** `admin@example.com`
- **Password:** `password123`

Change these in the `.env` file for production.

## API Integration

The dashboard communicates with the ETL API using the `APIClient` class in `api_client.py`. All endpoints are RESTful and require authentication with a Bearer token.

### Available Endpoints

- Users: `GET /users`, `POST /users`, `PUT /users/{id}`, `DELETE /users/{id}`
- Roles: `GET /roles`, `POST /roles`, `PUT /roles/{id}`, `DELETE /roles/{id}`
- Uploads: `GET /uploads`, `POST /uploads`, `GET /uploads/{id}/logs`
- Data Models: `GET /data-models`, `POST /data-models`, `PUT /data-models/{id}`, `DELETE /data-models/{id}`
- Organizations: `GET /organizations`, `GET /organizations/{id}`

## Troubleshooting

### API Connection Error
- Ensure the ETL API is running on the configured URL
- Check that `API_URL` in `.env` is correct
- Verify network connectivity

### Authentication Failed
- Verify `ADMIN_EMAIL` and `ADMIN_PASSWORD` in `.env`
- Ensure the user exists in the database
- Check ETL API logs for authentication errors

## License

This project is part of the BI Dashboards Builder application.
