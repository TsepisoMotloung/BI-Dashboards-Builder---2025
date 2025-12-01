# ETL Pipeline API Guide

Complete guide for using the ETL Pipeline REST API.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All endpoints except `/auth/register` and `/auth/login` require authentication using JWT Bearer tokens.

### Get Token

**Endpoint**: `POST /auth/login`

```bash
curl -X POST "https://zany-space-lamp-rvgjjwrgv7jfwwjv-8000.app.github.dev/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }'
```

**Response**:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### Using the Token

Include the token in the Authorization header:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v1/users/me
```

## API Endpoints

### 1. Authentication

#### Register New User
```bash
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "full_name": "John Doe",
  "password": "securepassword"
}
```

#### Login
```bash
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

### 2. Users

#### Get Current User
```bash
GET /users/me
Authorization: Bearer TOKEN
```

#### List All Users
```bash
GET /users?skip=0&limit=100
Authorization: Bearer TOKEN
```

#### Get User by ID
```bash
GET /users/{user_id}
Authorization: Bearer TOKEN
```

#### Update User
```bash
PUT /users/{user_id}
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "full_name": "Updated Name",
  "status": "active"
}
```

### 3. Data Models

#### Create Data Model
```bash
POST /data-models
Authorization: Bearer TOKEN
Content-Type: application/json

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
        "name": "category",
        "type": "string",
        "max_length": 100
      },
      {
        "name": "in_stock",
        "type": "boolean",
        "default": true
      }
    ],
    "indexes": ["product_name", "category"]
  }
}
```

**Field Types**:
- `string` - Variable length text (max_length supported)
- `integer` - Whole numbers
- `float` - Decimal numbers  
- `boolean` - True/False
- `date` - Date only
- `datetime` - Date and time
- `text` - Long text

#### List Data Models
```bash
GET /data-models?skip=0&limit=100
Authorization: Bearer TOKEN
```

#### Get Data Model by ID
```bash
GET /data-models/{model_id}
Authorization: Bearer TOKEN
```

#### Get Data Model by Name
```bash
GET /data-models/name/{model_name}
Authorization: Bearer TOKEN
```

#### Update Data Model
```bash
PUT /data-models/{model_id}
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "schema_definition": {
    "fields": [...]
  }
}
```

#### Delete Data Model
```bash
DELETE /data-models/{model_id}
Authorization: Bearer TOKEN
```

#### Create Relationship
```bash
POST /data-models/relationships
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "source_model_id": 1,
  "target_model_id": 2,
  "type": "1:N",
  "source_field": "category_id",
  "target_field": "id"
}
```

**Relationship Types**:
- `1:1` - One-to-One
- `1:N` - One-to-Many
- `N:M` - Many-to-Many

### 4. Uploads

#### Preview File
```bash
POST /uploads/preview
Authorization: Bearer TOKEN
Content-Type: multipart/form-data

--form 'file=@/path/to/data.xlsx'
```

**Response**:
```json
{
  "headers": ["product_name", "price", "category"],
  "sample_data": [
    {"product_name": "Widget", "price": 19.99, "category": "Tools"},
    ...
  ],
  "total_rows": 1000,
  "detected_types": {
    "product_name": "string",
    "price": "float",
    "category": "string"
  }
}
```

#### Upload Data
```bash
POST /uploads
Authorization: Bearer TOKEN
Content-Type: multipart/form-data

--form 'file=@/path/to/data.xlsx' \
--form 'upload_request={
  "model_id": 1,
  "column_mappings": [
    {
      "file_column": "Product Name",
      "model_field": "product_name"
    },
    {
      "file_column": "Price ($)",
      "model_field": "price"
    },
    {
      "file_column": "Category",
      "model_field": "category"
    }
  ],
  "skip_rows": 0,
  "validate_only": false
}'
```

#### List Upload History
```bash
GET /uploads?model_id=1&skip=0&limit=100
Authorization: Bearer TOKEN
```

#### Get Upload by ID
```bash
GET /uploads/{upload_id}
Authorization: Bearer TOKEN
```

#### Rollback Upload
```bash
POST /uploads/{upload_id}/rollback
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "upload_id": 123,
  "reason": "Incorrect data uploaded"
}
```

## Complete Workflow Example

### 1. Login
```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' \
  | jq -r '.access_token')
```

### 2. Create Data Model
```bash
curl -X POST "http://localhost:8000/api/v1/data-models" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sales",
    "schema_definition": {
      "fields": [
        {"name": "date", "type": "date", "required": true},
        {"name": "amount", "type": "float", "required": true},
        {"name": "customer", "type": "string", "max_length": 255}
      ]
    }
  }'
```

### 3. Preview File
```bash
curl -X POST "http://localhost:8000/api/v1/uploads/preview" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sales_data.xlsx"
```

### 4. Upload Data
```bash
curl -X POST "http://localhost:8000/api/v1/uploads" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sales_data.xlsx" \
  -F 'upload_request={
    "model_id": 1,
    "column_mappings": [
      {"file_column": "Date", "model_field": "date"},
      {"file_column": "Amount", "model_field": "amount"},
      {"file_column": "Customer Name", "model_field": "customer"}
    ]
  }'
```

### 5. Check Upload Status
```bash
curl -X GET "http://localhost:8000/api/v1/uploads/1" \
  -H "Authorization: Bearer $TOKEN"
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Error message describing what went wrong"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid authentication credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "User account is not active"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "message": "Detailed error message"
}
```

## Rate Limiting

Currently no rate limiting is implemented. In production, consider implementing:
- Rate limiting per IP
- Rate limiting per user
- Request throttling

## Best Practices

1. **Always validate data** before uploading using the preview endpoint
2. **Use meaningful names** for data models (alphanumeric with underscores)
3. **Define constraints** properly (required fields, max_length, etc.)
4. **Test with small datasets** first before uploading large files
5. **Monitor upload status** and check for errors
6. **Keep tokens secure** and refresh regularly
7. **Use HTTPS** in production

## Support

For issues or questions:
- Check logs in the application
- Review error messages carefully
- Consult API documentation at `/api/docs`
