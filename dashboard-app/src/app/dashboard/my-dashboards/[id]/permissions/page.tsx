import { auth } from "@/auth"
import { redirect } from "next/navigation"
import { prisma } from "@/lib/prisma"
import { DashboardLayout } from "@/components/layout/DashboardLayout"
import Link from "next/link"
import { Button } from "@/components/ui/Button"
import { DashboardPermissionsManager } from "@/components/DashboardPermissionsManager"

export default async function DashboardPermissionsPage({ params }: { params: { id: string } }) {
  const session = await auth()
  if (!session?.user?.id) redirect("/auth/signin")

  const dashboardId = parseInt(params.id)
  if (isNaN(dashboardId)) redirect("/dashboard/my-dashboards")

  const dashboard = await prisma.dashboard.findUnique({
    where: { id: dashboardId },
    include: { permissions: { include: { role: true } } },
  })

  if (!dashboard) {
    redirect("/dashboard/my-dashboards")
  }

  // Only creator can manage permissions
  if (dashboard.created_by !== session.user.id) {
    redirect(`/dashboard/viewer/${dashboardId}`)
  }

  const roles = await prisma.role.findMany({ orderBy: { name: "asc" } })

  const initialPermissions = dashboard.permissions.map((p) => ({
    dashboard_id: p.dashboard_id,
    role_id: p.role_id,
    permissions_json: p.permissions_json,
    role: { id: p.role.id, name: p.role.name },
  }))

  return (
    <DashboardLayout user={session.user}>
      <div className="max-w-4xl mx-auto py-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold">Manage Access — {dashboard.name}</h2>
            <p className="text-sm text-gray-600">Grant or revoke role access to this dashboard</p>
          </div>
          <div className="flex gap-2">
            <Link href={`/dashboard/my-dashboards/${dashboardId}`}>
              <Button variant="ghost">Back</Button>
            </Link>
          </div>
        </div>

        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold mb-2">Available Roles</h3>
            <DashboardPermissionsManager dashboardId={dashboardId} roles={roles.map(r=>({id:r.id,name:r.name}))} initialPermissions={initialPermissions} />
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
