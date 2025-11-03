# Dashboard Application - Quick Start Guide

## ✅ Current Status

**Foundation Complete**: Authentication, layouts, and core pages built!

### What's Working Now

✅ User authentication (compatible with ETL app)
✅ Dashboard layout with sidebar navigation
✅ User profile page
✅ Admin users management page
✅ Data models listing page
✅ Role-based navigation
✅ Responsive UI components

## 🚀 Setup Steps

### 1. Install Dependencies

```bash
npm install
```

Expected packages:
- next@^14.2.0
- next-auth@^5.0.0-beta.19
- @prisma/client@^5.14.0
- argon2@^0.31.0 (ETL compatibility!)
- plotly.js, tailwindcss, and more

### 2. Configure Environment

```bash
# .env file should already exist
# Verify it has correct values:

DATABASE_URL="mysql://root:YOUR_PASSWORD@localhost:3306/bi_dashboard"
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="generate-a-strong-secret-key"
ETL_API_URL="http://localhost:8000/api/v1"
```

**Generate NEXTAUTH_SECRET**:
```bash
openssl rand -base64 32
```

### 3. Ensure Database is Ready

The database should already be initialized via ETL app:

```bash
cd ../etl-app
python init_db.py
```

This creates:
- All 15 tables
- Default roles and permissions
- Super admin user (admin@example.com / admin123)

### 4. Generate Prisma Client

```bash
npx prisma generate
```

This creates the TypeScript client for database access.

### 5. Run Development Server

```bash
npm run dev
```

Application starts at: http://localhost:3000

## 🧪 Testing the Application

### Test 1: Login

1. Open http://localhost:3000
2. Should redirect to http://localhost:3000/auth/signin
3. Login with:
   - Email: admin@example.com
   - Password: admin123
4. Should redirect to dashboard

✅ **Success**: You see the dashboard home page with stats!

### Test 2: Navigation

Click through the sidebar:
- ✅ Dashboard (home)
- ✅ Data Models
- ✅ Users (admin only)
- ✅ Settings → Profile

### Test 3: Profile Page

1. Click user avatar in top-right
2. Click "Profile"
3. Should see:
   - Your user information
   - Assigned roles (Super Admin)
   - Account activity stats

✅ **Success**: Profile loads with your information!

### Test 4: Admin Pages

As admin user:
1. Click "Users" in sidebar
2. Should see list of all users
3. Stats should show user counts

✅ **Success**: Admin pages accessible and loading data!

### Test 5: Role-Based Navigation

The sidebar should show different items based on roles:
- **Super Admin**: All items visible
- **Admin**: Most items (no Roles & Permissions)
- **Standard User**: Limited items

## 📁 Pages Created

### Public
- ✅ `/auth/signin` - Login page

### Dashboard
- ✅ `/dashboard` - Home page with stats
- ✅ `/dashboard/settings/profile` - User profile
- ✅ `/dashboard/admin/users` - User management
- ✅ `/dashboard/data-models` - Data models listing

### Pending (Next Chunk)
- ⏳ `/dashboard/my-dashboards` - Dashboard viewer
- ⏳ `/dashboard/uploads` - Upload management
- ⏳ `/dashboard/admin/roles` - Role management
- ⏳ `/dashboard/admin/audit` - Audit logs

## 🎨 UI Components Available

### Layout Components
- ✅ `Sidebar` - Navigation menu
- ✅ `Header` - Top bar with user menu
- ✅ `DashboardLayout` - Complete layout wrapper

### UI Components
- ✅ `Button` - Multiple variants (default, outline, ghost, etc.)
- ✅ `Card` - With header, content, footer
- ✅ `Badge` - Status indicators
- ✅ `Avatar` - User avatars with initials

## 🔧 Common Issues

### Issue: "Cannot find module '@prisma/client'"

**Fix**:
```bash
npx prisma generate
```

### Issue: "Database connection failed"

**Check**:
1. MySQL is running
2. Database `bi_dashboard` exists
3. Credentials in .env are correct
4. ETL app can connect (test there first)

### Issue: "NextAuth error"

**Check**:
1. NEXTAUTH_SECRET is set in .env
2. NEXTAUTH_URL matches your app URL
3. Session strategy is "jwt" in auth.ts

### Issue: "User not found" after login

**Check**:
1. ETL app initialized database
2. Admin user exists: admin@example.com
3. User status is "active" in database

### Issue: "Page not found"

**Remember**: Only these pages exist so far:
- /auth/signin ✅
- /dashboard ✅
- /dashboard/settings/profile ✅
- /dashboard/admin/users ✅
- /dashboard/data-models ✅

Other pages will return 404 until built.

## 📊 Database Queries Examples

The app uses Prisma for type-safe queries:

```typescript
// Get user with roles
const user = await prisma.user.findUnique({
  where: { id: userId },
  include: {
    user_roles: {
      include: { role: true }
    }
  }
})

// Get all data models with upload count
const models = await prisma.dataModel.findMany({
  include: {
    upload_history: {
      select: { id: true }
    }
  }
})

// Count active users
const activeUsers = await prisma.user.count({
  where: { status: 'active' }
})
```

## 🎯 What's Next (Chunk 6)

Will build:
1. **Dashboard Viewer** - View and interact with dashboards
2. **Visualizations** - Plotly.js chart components
3. **Upload Management** - File upload interface
4. **ETL API Integration** - Connect to backend API
5. **Dashboard Builder** - Create/edit dashboards (admin)

## 🔍 File Structure Reference

```
src/
├── app/
│   ├── api/auth/[...nextauth]/  # NextAuth handlers
│   ├── auth/signin/             # Login page
│   ├── dashboard/               # Dashboard pages
│   │   ├── page.tsx            # Home ✅
│   │   ├── loading.tsx         # Loading state ✅
│   │   ├── settings/profile/   # Profile ✅
│   │   ├── admin/users/        # User mgmt ✅
│   │   └── data-models/        # Models ✅
│   ├── layout.tsx              # Root layout
│   └── page.tsx                # Home redirect
├── components/
│   ├── layout/                 # Layout components
│   │   ├── Sidebar.tsx        # Navigation ✅
│   │   ├── Header.tsx         # Top bar ✅
│   │   └── DashboardLayout.tsx # Wrapper ✅
│   └── ui/                     # UI components
│       ├── Button.tsx         # Button ✅
│       ├── Card.tsx           # Card ✅
│       ├── Badge.tsx          # Badge ✅
│       └── Avatar.tsx         # Avatar ✅
├── lib/                        # Utilities
└── types/                      # TypeScript types
```

## ✅ Verification Checklist

Before proceeding to next chunk:

- [ ] npm install completed successfully
- [ ] .env file configured
- [ ] Prisma client generated
- [ ] Development server starts
- [ ] Can access signin page
- [ ] Can login with admin credentials
- [ ] Dashboard loads with stats
- [ ] Can navigate between pages
- [ ] Profile page loads correctly
- [ ] Admin users page loads (for admin)
- [ ] Data models page loads
- [ ] User menu works
- [ ] Logout works

## 🎉 Success Metrics

You should now have:
- ✅ Working authentication
- ✅ Complete dashboard layout
- ✅ 5 functional pages
- ✅ Role-based navigation
- ✅ User management (admin)
- ✅ Profile management
- ✅ Database integration
- ✅ Responsive UI

**The foundation is solid and ready for visualizations!** 🚀

## 📝 Notes

- All pages use Server Components by default
- Client Components marked with "use client"
- Database queries happen on server
- Prisma provides full type safety
- Authentication via NextAuth.js v5
- Argon2 passwords compatible with ETL app

## 🆘 Need Help?

1. Check browser console for errors
2. Check terminal for server errors
3. Verify database connection
4. Review .env configuration
5. Ensure ETL app database is initialized
6. Check Prisma client is generated

Most issues are configuration-related. Double-check environment variables!
