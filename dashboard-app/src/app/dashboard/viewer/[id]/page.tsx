import { auth } from "@/auth"
import { redirect } from "next/navigation"
import { prisma } from "@/lib/prisma"
import { DashboardLayout } from "@/components/layout/DashboardLayout"
import { Card, CardContent } from "@/components/ui/Card"
import Link from "next/link"
import { Button } from "@/components/ui/Button"
import DashboardViewer from "@/components/DashboardViewer"

export default async function DashboardViewerPage({
  params,
}: {
  params: { id: string }
}) {
  const session = await auth()
  if (!session?.user?.id) {
    redirect("/auth/signin")
  }

  const dashboardId = parseInt(params.id)
  if (isNaN(dashboardId)) {
    return (
      <DashboardLayout user={session.user}>
        <div className="p-8">
          <h1 className="text-2xl font-bold mb-4">Invalid dashboard ID</h1>
          <Link href="/dashboard/my-dashboards">
            <Button>Back to Dashboards</Button>
          </Link>
        </div>
      </DashboardLayout>
    )
  }

  // Fetch dashboard - must be published
  const dashboard = await prisma.dashboard.findUnique({
    where: { id: dashboardId },
    include: {
      tabs: {
        include: { visualizations: true },
        orderBy: { order: "asc" },
      },
      creator: { select: { full_name: true } },
      permissions: true,
    },
  })

  if (!dashboard) {
    return (
      <DashboardLayout user={session.user}>
        <div className="p-8">
          <h1 className="text-2xl font-bold mb-4">Dashboard not found</h1>
          <Link href="/dashboard/my-dashboards">
            <Button>Back to Dashboards</Button>
          </Link>
        </div>
      </DashboardLayout>
    )
  }

  if (!dashboard.is_published) {
    return (
      <DashboardLayout user={session.user}>
        <div className="p-8">
          <h1 className="text-2xl font-bold mb-4">Dashboard not published</h1>
          <p className="text-gray-600 mb-4">
            This dashboard is not published yet.
          </p>
          <Link href="/dashboard/my-dashboards">
            <Button>Back to Dashboards</Button>
          </Link>
        </div>
      </DashboardLayout>
    )
  }

  // Check user permissions
  // Creator has full access
  const isCreator = dashboard.created_by === session.user.id

  // Check if user has role-based access
  let hasAccess = isCreator
  let userPermission = null

  if (!hasAccess && session.user.roles) {
    const userRoleIds = (session.user.roles as any[]).map((r: any) => r.id)
    const permission = dashboard.permissions.find((p) =>
      userRoleIds.includes(p.role_id)
    )
    if (permission) {
      hasAccess = true
      userPermission = permission
    }
  }

  if (!hasAccess) {
    return (
      <DashboardLayout user={session.user}>
        <div className="p-8">
          <Card>
            <CardContent className="pt-8">
              <div className="text-center">
                <h1 className="text-2xl font-bold mb-2">Access Denied</h1>
                <p className="text-gray-600 mb-4">
                  You don't have permission to view this dashboard.
                </p>
                <Link href="/dashboard/my-dashboards">
                  <Button>Back to Dashboards</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout user={session.user}>
      <div className="flex flex-col h-screen bg-white">
        {/* Header */}
        <div className="border-b border-gray-200 p-4 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{dashboard.name}</h1>
            <p className="text-sm text-gray-500 mt-1">
              {dashboard.description}
            </p>
          </div>

          <Link href="/dashboard/my-dashboards">
            <Button variant="secondary">Back to Dashboards</Button>
          </Link>
        </div>

        {/* Viewer Component */}
        <DashboardViewer
          dashboard={dashboard}
          userPermission={userPermission}
          isCreator={isCreator}
        />
      </div>
    </DashboardLayout>
  )
}
