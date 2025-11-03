import { auth } from "@/auth"
import { redirect } from "next/navigation"
import { DashboardLayout } from "@/components/layout/DashboardLayout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"
import { BarChart3, Database, Upload, Users } from "lucide-react"
import { prisma } from "@/lib/prisma"

export default async function DashboardPage() {
  const session = await auth()

  if (!session) {
    redirect("/auth/signin")
  }

  // Get statistics
  const [dataModelsCount, uploadsCount, usersCount, dashboardsCount] = await Promise.all([
    prisma.dataModel.count(),
    prisma.uploadHistory.count({
      where: { user_id: session.user.id }
    }),
    prisma.user.count(),
    prisma.dashboard.count(),
  ])

  const stats = [
    {
      title: "Data Models",
      value: dataModelsCount,
      description: "Available data models",
      icon: Database,
      color: "text-blue-600",
    },
    {
      title: "My Uploads",
      value: uploadsCount,
      description: "Files uploaded by you",
      icon: Upload,
      color: "text-green-600",
    },
    {
      title: "Total Users",
      value: usersCount,
      description: "Registered users",
      icon: Users,
      color: "text-purple-600",
    },
    {
      title: "Dashboards",
      value: dashboardsCount,
      description: "Available dashboards",
      icon: BarChart3,
      color: "text-orange-600",
    },
  ]

  return (
    <DashboardLayout user={session.user}>
      <div className="space-y-6">
        {/* Welcome Section */}
        <div>
          <h2 className="text-3xl font-bold tracking-tight">
            Welcome back, {session.user.name?.split(" ")[0] || "User"}!
          </h2>
          <p className="text-muted-foreground">
            Here's what's happening with your data today.
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat) => (
            <Card key={stat.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.title}
                </CardTitle>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground">
                  {stat.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>
              Common tasks and shortcuts
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              <a
                href="/dashboard/my-dashboards"
                className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-6 hover:border-primary transition-colors"
              >
                <BarChart3 className="h-8 w-8 text-primary mb-2" />
                <h3 className="font-medium">View Dashboards</h3>
                <p className="text-xs text-muted-foreground text-center">
                  Access your dashboards
                </p>
              </a>

              <a
                href="/dashboard/uploads"
                className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-6 hover:border-primary transition-colors"
              >
                <Upload className="h-8 w-8 text-primary mb-2" />
                <h3 className="font-medium">Upload Data</h3>
                <p className="text-xs text-muted-foreground text-center">
                  Import new data files
                </p>
              </a>

              <a
                href="/dashboard/data-models"
                className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-6 hover:border-primary transition-colors"
              >
                <Database className="h-8 w-8 text-primary mb-2" />
                <h3 className="font-medium">Data Models</h3>
                <p className="text-xs text-muted-foreground text-center">
                  Manage data structures
                </p>
              </a>
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Uploads</CardTitle>
            <CardDescription>
              Your latest data uploads
            </CardDescription>
          </CardHeader>
          <CardContent>
            {uploadsCount > 0 ? (
              <RecentUploads userId={session.user.id} />
            ) : (
              <p className="text-sm text-muted-foreground">
                No uploads yet. Upload your first data file to get started.
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}

async function RecentUploads({ userId }: { userId: number }) {
  const uploads = await prisma.uploadHistory.findMany({
    where: { user_id: userId },
    include: {
      data_model: true,
    },
    orderBy: { created_at: "desc" },
    take: 5,
  })

  return (
    <div className="space-y-4">
      {uploads.map((upload) => (
        <div key={upload.id} className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium">{upload.file_name}</p>
            <p className="text-xs text-muted-foreground">
              {upload.data_model.name} • {upload.records_count} records
            </p>
          </div>
          <div className="text-right">
            <span
              className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                upload.status === "completed"
                  ? "bg-green-100 text-green-800"
                  : upload.status === "failed"
                  ? "bg-red-100 text-red-800"
                  : "bg-yellow-100 text-yellow-800"
              }`}
            >
              {upload.status}
            </span>
            <p className="text-xs text-muted-foreground mt-1">
              {new Date(upload.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>
      ))}
    </div>
  )
}
