import { auth } from "@/auth"
import { redirect } from "next/navigation"
import { DashboardLayout } from "@/components/layout/DashboardLayout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Avatar } from "@/components/ui/Avatar"
import { getInitials, formatDateTime } from "@/lib/utils"
import { prisma } from "@/lib/prisma"
import { Mail, Calendar, Shield, Building } from "lucide-react"

export default async function ProfilePage() {
  const session = await auth()

  if (!session) {
    redirect("/auth/signin")
  }

  // Get full user data with roles
  const user = await prisma.user.findUnique({
    where: { id: session.user.id },
    include: {
      user_roles: {
        include: {
          role: true,
        },
      },
    },
  })

  if (!user) {
    redirect("/dashboard")
  }

  return (
    <DashboardLayout user={session.user}>
      <div className="space-y-6 max-w-4xl">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Profile</h2>
          <p className="text-muted-foreground">
            Manage your account information
          </p>
        </div>

        {/* Profile Overview */}
        <Card>
          <CardHeader>
            <CardTitle>Profile Information</CardTitle>
            <CardDescription>
              Your personal information and account details
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-start space-x-4">
              <Avatar
                fallback={getInitials(user.full_name)}
                className="h-20 w-20 text-lg"
              />
              <div className="flex-1 space-y-1">
                <h3 className="text-xl font-semibold">{user.full_name}</h3>
                <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                  <Mail className="h-4 w-4" />
                  <span>{user.email}</span>
                </div>
                <div className="flex items-center space-x-2 pt-2">
                  <Badge
                    variant={
                      user.status === "active"
                        ? "success"
                        : user.status === "pending"
                        ? "secondary"
                        : "destructive"
                    }
                  >
                    {user.status}
                  </Badge>
                </div>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2 pt-4 border-t">
              <div className="space-y-2">
                <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                  <Calendar className="h-4 w-4" />
                  <span className="font-medium">Member Since</span>
                </div>
                <p className="text-sm">{formatDateTime(user.created_at)}</p>
              </div>

              <div className="space-y-2">
                <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                  <Calendar className="h-4 w-4" />
                  <span className="font-medium">Last Updated</span>
                </div>
                <p className="text-sm">{formatDateTime(user.updated_at)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Roles & Permissions */}
        <Card>
          <CardHeader>
            <CardTitle>Roles & Permissions</CardTitle>
            <CardDescription>
              Your assigned roles in the system
            </CardDescription>
          </CardHeader>
          <CardContent>
            {user.user_roles.length > 0 ? (
              <div className="space-y-4">
                {user.user_roles.map((ur) => (
                  <div
                    key={ur.role_id}
                    className="flex items-start justify-between rounded-lg border p-4"
                  >
                    <div className="flex items-start space-x-3">
                      <Shield className="h-5 w-5 text-primary mt-0.5" />
                      <div>
                        <h4 className="font-medium">{ur.role.name}</h4>
                        <p className="text-sm text-muted-foreground">
                          {ur.role.description}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          Assigned: {formatDateTime(ur.assigned_at)}
                        </p>
                      </div>
                    </div>
                    <Badge variant={ur.role.is_system_role ? "secondary" : "default"}>
                      {ur.role.is_system_role ? "System Role" : "Custom"}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                No roles assigned yet. Contact your administrator.
              </p>
            )}
          </CardContent>
        </Card>

        {/* Account Stats */}
        <Card>
          <CardHeader>
            <CardTitle>Activity Summary</CardTitle>
            <CardDescription>
              Your activity on the platform
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ActivityStats userId={user.id} />
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}

async function ActivityStats({ userId }: { userId: number }) {
  const [uploadsCount, dashboardsCount] = await Promise.all([
    prisma.uploadHistory.count({ where: { user_id: userId } }),
    prisma.dashboard.count({ where: { created_by: userId } }),
  ])

  const stats = [
    { label: "Total Uploads", value: uploadsCount },
    { label: "Dashboards Created", value: dashboardsCount },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {stats.map((stat) => (
        <div key={stat.label} className="rounded-lg border p-4">
          <p className="text-sm text-muted-foreground">{stat.label}</p>
          <p className="text-2xl font-bold">{stat.value}</p>
        </div>
      ))}
    </div>
  )
}
