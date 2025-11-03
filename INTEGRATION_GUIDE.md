# BI Dashboard System - Integration Guide

## Overview

This system consists of two integrated applications sharing a single MySQL database:

1. **ETL Application** (FastAPI/Python) - Port 8000
2. **Dashboard Application** (Next.js/TypeScript) - Port 3000

## Shared Database Architecture

Both applications connect to the **same MySQL database**: `bi_dashboard`

### Why This Matters

✅ **Single Source of Truth**: User data, roles, and permissions are stored once
✅ **No Sync Issues**: Changes in one app are immediately visible in the other
✅ **Simplified Management**: One database to backup, maintain, and secure
✅ **Seamless Integration**: Users created in either app work in both

## Database Tables (15 Total)

### User Management
- `users` - User accounts with Argon2-hashed passwords
- `roles` - System roles (Super Admin, Admin, Standard User)
- `permissions` - Granular permissions
- `role_permissions` - Role-to-permission mapping
- `user_roles` - User-to-role assignment

### Organization
- `organizational_units` - Company hierarchy
- `user_organizational_units` - User org assignments

### Data Models (ETL)
- `data_models` - Dynamic entity definitions
- `data_relationships` - Inter-model relationships
- `upload_history` - Upload tracking

### Dashboards
- `dashboards` - Dashboard configurations
- `dashboard_tabs` - Dashboard tabs
- `visualizations` - Chart definitions
- `dashboard_permissions` - Dashboard access control

### Auditing
- `audit_logs` - System activity tracking

## Authentication Flow

### Users Created in ETL App

1. User registers via ETL API: `POST /api/v1/auth/register`
2. Password hashed with **Argon2** and stored in database
3. User record created with `status='pending'`
4. Admin activates user (changes status to 'active')
5. **User can now log in to both apps**:
   - ETL App: Uses Argon2 verification
   - Dashboard App: Uses Argon2 verification (via argon2 library)

### Users Created in Dashboard App (Future)

1. User registers via Dashboard UI
2. Password hashed with **Argon2** (for consistency)
3. Stored in same `users` table
4. **User can log in to both apps**

### Password Verification

Both applications support Argon2:

**ETL App (Python)**:
```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
pwd_context.verify(password, hash)
```

**Dashboard App (TypeScript)**:
```typescript
import argon2 from 'argon2'
await argon2.verify(hash, password)
```

## Setup Instructions

### Prerequisites

1. **MySQL 8.0+** installed and running
2. **Python 3.11+** for ETL app
3. **Node.js 18+** for Dashboard app

### Step 1: Create Database

```bash
mysql -u root -p
```

```sql
CREATE DATABASE bi_dashboard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Step 2: Configure ETL Application

```bash
cd etl-app

# Create environment file
cp .env.example .env

# Edit .env with your database credentials
# DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/bi_dashboard

# Install dependencies
pip install -r requirements.txt

# Initialize database (creates tables and seed data)
python init_db.py
```

This creates:
- All 15 database tables
- Default roles and permissions
- Super admin user (admin@example.com / admin123)

### Step 3: Configure Dashboard Application

```bash
cd dashboard-app

# Create environment file
cp .env.example .env

# Edit .env with SAME database credentials
# DATABASE_URL="mysql://root:YOUR_PASSWORD@localhost:3306/bi_dashboard"

# Install dependencies
npm install

# Generate Prisma client
npx prisma generate
```

### Step 4: Run Both Applications

**Terminal 1 - ETL App**:
```bash
cd etl-app
python run.py
```
- API: http://localhost:8000
- Docs: http://localhost:8000/api/docs

**Terminal 2 - Dashboard App**:
```bash
cd dashboard-app
npm run dev
```
- App: http://localhost:3000

### Step 5: Test Integration

1. Open Dashboard: http://localhost:3000
2. Sign in with: admin@example.com / admin123
3. **Success!** User created in ETL app works in Dashboard

## Configuration Files

### ETL App - .env
```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/bi_dashboard
SECRET_KEY=your-secret-key-here
UPLOAD_DIR=./uploads
TEMPLATE_DIR=./templates
```

### Dashboard App - .env
```env
DATABASE_URL="mysql://root:password@localhost:3306/bi_dashboard"
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="your-nextauth-secret"
ETL_API_URL="http://localhost:8000/api/v1"
```

⚠️ **Important**: Both apps must use the **same database connection string**

## API Integration

The Dashboard app can call ETL API endpoints:

```typescript
// Example: Fetch data models from ETL API
const response = await fetch(`${process.env.ETL_API_URL}/data-models`, {
  headers: {
    'Authorization': `Bearer ${etl_token}`
  }
})
```

Note: ETL API uses its own JWT tokens. Future enhancement could unify tokens.

## Development Workflow

### Scenario 1: Testing User Creation

1. Create user via ETL API:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "full_name": "Test User",
    "password": "password123"
  }'
```

2. Activate user (set status to 'active' in database or via admin)

3. Log in to Dashboard at http://localhost:3000 with same credentials

### Scenario 2: Testing Role Assignment

1. Assign role via ETL API:
```bash
curl -X POST http://localhost:8000/api/v1/users/1/roles/2 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

2. Log out and back in to Dashboard

3. New role appears in session

### Scenario 3: Data Model & Upload

1. Create data model via ETL API
2. Upload data via ETL API
3. View data in Dashboard visualizations

## Database Migrations

### Adding New Columns/Tables

1. **Update ETL App** (SQLAlchemy models)
2. **Update Dashboard App** (Prisma schema)
3. **Generate migration**:
   ```bash
   cd etl-app
   alembic revision --autogenerate -m "description"
   alembic upgrade head
   ```
4. **Regenerate Prisma client**:
   ```bash
   cd dashboard-app
   npx prisma generate
   ```

## Security Considerations

### Passwords
✅ Both apps use Argon2 (industry standard)
✅ Hashes are compatible between apps
✅ No plaintext passwords stored

### Sessions
- ETL: JWT tokens (stateless)
- Dashboard: JWT via NextAuth (stateless)

### Database Access
- Both apps use connection pooling
- Prepared statements prevent SQL injection
- ORM layer (SQLAlchemy/Prisma) adds protection

## Troubleshooting

### Issue: Dashboard can't log in with ETL-created user

**Check**:
1. Is user status 'active' in database?
2. Is argon2 package installed in Dashboard? (`npm list argon2`)
3. Are database credentials correct in both .env files?

### Issue: Password verification fails

**Check**:
1. Password hash starts with `$argon2`?
2. argon2 library installed and working?
3. Try creating new user to test

### Issue: Roles not appearing in Dashboard session

**Check**:
1. User has roles assigned in `user_roles` table?
2. JWT callback in auth.ts includes roles?
3. Try logging out and back in

### Issue: Database connection fails

**Check**:
1. MySQL service running?
2. Database exists? (`SHOW DATABASES;`)
3. User has permissions? (`GRANT ALL PRIVILEGES...`)
4. Connection string format correct?

## Production Deployment

### Checklist

- [ ] Change default admin password
- [ ] Generate strong SECRET_KEY (ETL)
- [ ] Generate strong NEXTAUTH_SECRET (Dashboard)
- [ ] Use production database URL
- [ ] Enable HTTPS for both apps
- [ ] Configure CORS properly
- [ ] Set up database backups
- [ ] Enable connection SSL
- [ ] Review security settings
- [ ] Set up monitoring/logging
- [ ] Configure firewall rules
- [ ] Test disaster recovery

### Recommended Architecture

```
┌─────────────────────┐
│   Load Balancer     │
│     (HTTPS)         │
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     │           │
┌────▼────┐ ┌───▼────┐
│Dashboard│ │  ETL   │
│Next.js  │ │FastAPI │
│Port 3000│ │Port8000│
└────┬────┘ └───┬────┘
     │          │
     └────┬─────┘
          │
     ┌────▼────┐
     │  MySQL  │
     │Database │
     └─────────┘
```

## Monitoring

### Key Metrics

**Database**:
- Connection pool usage
- Query performance
- Table sizes
- Index usage

**ETL App**:
- API response times
- Upload success rate
- Error rates
- Active users

**Dashboard**:
- Page load times
- Session duration
- Authentication success rate
- Chart render times

## Backup Strategy

### Database
```bash
# Daily backup
mysqldump -u root -p bi_dashboard > backup_$(date +%Y%m%d).sql

# Restore
mysql -u root -p bi_dashboard < backup_20250101.sql
```

### Uploads (ETL App)
```bash
tar -czf uploads_$(date +%Y%m%d).tar.gz etl-app/uploads/
```

## Next Steps

After completing the setup:

1. ✅ Test user login in both apps
2. ✅ Create test data model via ETL API
3. ✅ Upload sample data
4. 🔨 Build dashboard UI components (Next Chunk)
5. 🔨 Implement visualizations (Next Chunk)
6. 🔨 Add admin management pages (Next Chunk)

## Support

Both applications are fully documented:
- ETL App: See `etl-app/README.md`
- Dashboard: See `dashboard-app/README.md`
- API Guide: See `etl-app/API_GUIDE.md`
