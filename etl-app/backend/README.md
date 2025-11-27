# ETL Pipeline Application

Backend API for the Business Intelligence Dashboard System - handles data ingestion, transformation, and management.

## Features

- 🔐 **Authentication**: JWT-based authentication with role-based access control
- 📊 **Dynamic Data Models**: Create and manage data models on-the-fly
- 📤 **Data Ingestion**: Upload Excel/CSV files with validation and preview
- 🔄 **Data Transformation**: Column mapping, type conversion, and validation
- 📝 **Upload Management**: Track upload history and rollback capabilities
- 🔍 **Audit Logging**: Comprehensive activity tracking
- 🏗️ **Dynamic Tables**: Automatically create database tables from schemas

## Tech Stack

- **Framework**: FastAPI 0.109.0
- **ORM**: SQLAlchemy 2.0.25
- **Database**: MySQL 8.0+
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **File Processing**: pandas, openpyxl
- **Migrations**: Alembic 1.13.1

## Prerequisites

- Python 3.11+
- MySQL 8.0+
- pip

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

3. Initialize the database:
```bash
python init_db.py
```

This will:
- Create all database tables
- Initialize roles and permissions
- Create default super admin user

## Default Credentials

After initialization, you can log in with:
- **Email**: admin@example.com
- **Password**: admin123

⚠️ **Change these credentials immediately in production!**

## Running the Application

### Development Mode
```bash
python run.py
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/api/docs
- Health: http://localhost:8000/health

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token

### Users
- `GET /api/v1/users/me` - Get current user info
- `GET /api/v1/users` - List all users
- `GET /api/v1/users/{id}` - Get user by ID
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user
- `POST /api/v1/users/{id}/roles/{role_id}` - Assign role

### Data Models
- `POST /api/v1/data-models` - Create data model
- `GET /api/v1/data-models` - List all data models
- `GET /api/v1/data-models/{id}` - Get data model by ID
- `PUT /api/v1/data-models/{id}` - Update data model
- `DELETE /api/v1/data-models/{id}` - Delete data model
- `POST /api/v1/data-models/relationships` - Create relationship
- `GET /api/v1/data-models/{id}/relationships` - Get relationships

### Uploads
- `POST /api/v1/uploads/preview` - Preview file before upload
- `POST /api/v1/uploads` - Upload and process data
- `GET /api/v1/uploads` - List upload history
- `GET /api/v1/uploads/{id}` - Get upload by ID
- `POST /api/v1/uploads/{id}/rollback` - Rollback upload

## Project Structure

```
etl-app/
├── app/
│   ├── api/              # API route handlers
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── data_models.py
│   │   └── uploads.py
│   ├── core/             # Core configurations
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── deps.py
│   │   └── init_db.py
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   ├── utils/            # Utility functions
│   └── main.py           # FastAPI application
├── alembic/              # Database migrations
├── uploads/              # Uploaded files
├── templates/            # Generated templates
├── requirements.txt
├── .env
└── run.py
```

## Database Schema

The system uses a shared database with the following main tables:

- **users**: User accounts
- **roles**: User roles
- **permissions**: System permissions
- **data_models**: Dynamic data model definitions
- **upload_history**: Upload tracking
- **audit_logs**: Activity logging
- **dashboards**: Dashboard configurations

Plus dynamically created tables prefixed with `data_*`

## Creating a Data Model

Example request to create a data model:

```json
{
  "name": "Products",
  "schema_definition": {
    "fields": [
      {
        "name": "product_name",
        "type": "string",
        "required": true,
        "max_length": 255
      },
      {
        "name": "price",
        "type": "float",
        "required": true,
        "min_value": 0
      },
      {
        "name": "in_stock",
        "type": "boolean",
        "default": true
      }
    ],
    "indexes": ["product_name"]
  }
}
```

This will create a physical table `data_products` in the database.

## Uploading Data

1. First, preview the file:
```bash
curl -X POST "http://localhost:8000/api/v1/uploads/preview" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@data.xlsx"
```

2. Then upload with column mappings:
```bash
curl -X POST "http://localhost:8000/api/v1/uploads" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@data.xlsx" \
  -F 'upload_request={"model_id": 1, "column_mappings": [...]}'
```

## Environment Variables

```env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/bi_dashboard
SECRET_KEY=your-secret-key-change-in-production
UPLOAD_DIR=./uploads
TEMPLATE_DIR=./templates
MAX_UPLOAD_SIZE=104857600
ALLOWED_EXTENSIONS=xlsx,xls,csv
```

## Development

### Running Tests
```bash
pytest
```

### Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

## Security Considerations

1. Change default admin credentials
2. Use strong SECRET_KEY in production
3. Enable HTTPS in production
4. Configure CORS for specific origins
5. Implement rate limiting
6. Regular security audits

## License

Proprietary - All rights reserved
