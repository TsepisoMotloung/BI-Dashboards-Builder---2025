# BI Dashboard Application

Frontend application for the Business Intelligence Dashboard System - provides visualization, user management, and reporting interfaces.

## Features

- 🔐 **Authentication**: NextAuth.js v5 with database sessions
- 👥 **User Management**: Role-based access control (RBAC)
- 📊 **Dashboards**: Interactive data visualizations with Plotly.js
- 🎨 **Modern UI**: Built with Next.js 14 + TypeScript + Tailwind CSS
- 🔄 **Real-time Data**: Integration with ETL API
- 📱 **Responsive**: Mobile-friendly design
- 📄 **PDF Export**: Export dashboards and charts

## Tech Stack

- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: NextAuth.js v5 (Auth.js)
- **ORM**: Prisma (shared database with ETL app)
- **Visualization**: Plotly.js
- **Forms**: React Hook Form + Zod validation
- **PDF**: jsPDF + html2canvas

## Prerequisites

- Node.js 18+
- npm or yarn
- MySQL 8.0+ (shared with ETL app)
- ETL Application running (for API integration)

## Installation

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Generate Prisma client:
```bash
npx prisma generate
```

4. Ensure database is initialized (via ETL app):
```bash
cd ../etl-app
python init_db.py
```

## Environment Variables

```env
# Database (shared with ETL application)
DATABASE_URL="mysql://root:password@localhost:3306/bi_dashboard"

# NextAuth.js Configuration
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="your-secret-key"

# ETL API
ETL_API_URL="http://localhost:8000/api/v1"
```

## Running the Application

### Development Mode
```bash
npm run dev
```

Application will be available at: http://localhost:3000

### Production Build
```bash
npm run build
npm start
```

## Authentication

### Shared Database with ETL App

This application uses the **same database** as the ETL application, including the same user tables. This means:

✅ Users created in the ETL app can log in to the dashboard
✅ Passwords are hashed with Argon2 (compatible with ETL app)
✅ Both bcrypt and Argon2 hashes are supported
✅ Roles and permissions are shared

### Default Credentials

After initializing the database via the ETL app:
- **Email**: admin@example.com
- **Password**: admin123

⚠️ Change these credentials in production!

### Password Compatibility

The dashboard app supports both:
- **Argon2** hashes (created by ETL app)
- **Bcrypt** hashes (native to Next.js)

This ensures seamless authentication regardless of where the user was created.

## Project Structure

```
dashboard-app/
├── src/
│   ├── app/                    # Next.js app router
│   │   ├── api/               # API routes
│   │   ├── auth/              # Authentication pages
│   │   ├── dashboard/         # Dashboard pages
│   │   ├── admin/             # Admin pages
│   │   └── layout.tsx         # Root layout
│   ├── components/            # React components
│   │   ├── ui/               # UI components
│   │   ├── dashboard/        # Dashboard components
│   │   └── admin/            # Admin components
│   ├── lib/                   # Utility libraries
│   │   ├── prisma.ts         # Prisma client
│   │   ├── auth-utils.ts     # Auth utilities
│   │   └── utils.ts          # General utilities
│   ├── types/                 # TypeScript types
│   ├── styles/                # Global styles
│   └── auth.ts                # NextAuth configuration
├── prisma/
│   └── schema.prisma          # Database schema
├── public/                    # Static files
└── package.json
```

## Database Schema

The Prisma schema mirrors the SQLAlchemy models from the ETL app, ensuring complete compatibility. The shared tables include:

- **users** - User accounts
- **roles** - User roles
- **permissions** - System permissions
- **dashboards** - Dashboard configurations
- **visualizations** - Chart configurations
- **data_models** - Dynamic data models
- **upload_history** - Upload tracking
- **audit_logs** - Activity logs

## NextAuth.js v5 Integration

### Configuration

NextAuth.js v5 is configured in `src/auth.ts` with:
- Credentials provider for email/password login
- JWT session strategy
- Custom callbacks for user data
- Prisma adapter for session management

### Session Data

The session includes:
```typescript
{
  user: {
    id: number
    email: string
    name: string
    status: UserStatus
    roles: string[]
  }
}
```

### Protected Routes

All routes except `/auth/*` require authentication via middleware.

### Role-Based Access

Utility functions for role checking:
```typescript
isAdmin(roles)           // Check if user is admin
hasRole(roles, role)     // Check specific role
hasAnyRole(roles, list)  // Check any role in list
```

## API Integration

The dashboard integrates with the ETL API for:
- Data model management
- Upload operations
- Data querying
- Analytics

Example API call:
```typescript
const response = await fetch(`${process.env.ETL_API_URL}/data-models`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
```

## Features by Role

### Super Admin
- Full system access
- User management
- Role assignment
- Dashboard creation and editing
- System configuration
- Audit log viewing

### Admin
- User management (view, create, edit)
- Dashboard management
- Data model management
- Upload management
- Limited audit access

### Standard User
- View assigned dashboards
- Upload data to assigned models
- Export dashboards
- View own upload history

## Development

### Adding New Pages

1. Create page in `src/app/[route]/page.tsx`
2. Add to middleware if auth required
3. Create components in `src/components/`

### Adding New API Routes

1. Create route in `src/app/api/[route]/route.ts`
2. Use Prisma for database access
3. Add proper error handling

### Styling

Uses Tailwind CSS with custom design system:
- Primary color: Blue (#3B82F6)
- Consistent spacing and typography
- Responsive breakpoints
- Dark mode ready (variables defined)

## Testing

```bash
# Type checking
npm run type-check

# Linting
npm run lint

# Build test
npm run build
```

## Production Deployment

### Prerequisites
1. Set strong NEXTAUTH_SECRET
2. Configure production DATABASE_URL
3. Set up HTTPS
4. Configure CORS for ETL API

### Build
```bash
npm run build
```

### Deploy
Compatible with:
- Vercel
- Docker
- Node.js servers
- Any platform supporting Next.js

### Environment
Ensure all production environment variables are set:
- DATABASE_URL (production database)
- NEXTAUTH_URL (production URL)
- NEXTAUTH_SECRET (strong random string)
- ETL_API_URL (production ETL API)

## Security

✅ Password hashing (Argon2/bcrypt)
✅ JWT sessions
✅ CSRF protection
✅ SQL injection protection (Prisma)
✅ XSS protection (React)
✅ Role-based access control
✅ Secure headers (Next.js)

## Performance

✅ Server-side rendering
✅ Automatic code splitting
✅ Image optimization
✅ API route caching
✅ Database connection pooling

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## Documentation

- NextAuth.js: https://authjs.dev
- Next.js: https://nextjs.org
- Prisma: https://prisma.io
- Plotly.js: https://plotly.com/javascript

## Support

For issues or questions:
- Check ETL app is running
- Verify database connection
- Review environment variables
- Check browser console for errors

## License

Proprietary - All rights reserved
