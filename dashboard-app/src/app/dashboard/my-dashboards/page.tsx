import { auth } from "@/auth"
import { redirect } from "next/navigation"
import { DashboardLayout } from "@/components/layout/DashboardLayout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Button } from "@/components/ui/Button"
import { prisma } from "@/lib/prisma"
import { formatDateTime, isAdmin } from "@/lib/utils"
import { BarChart3, Plus, Eye, Edit, Trash } from "lucide-react"
import Link from "next/link"

export default async function MyDashboardsPage() {
  const session = await auth()

  if (!session) {
    redirect("/auth/signin")
  }

  // Get user's accessible dashboards
  // For now, show all dashboards - in production, filter by permissions
  const dashboards = await prisma.dashboard.findMany({
    include: {
      creator: {
        select: {
          full_name: true,
          email: true,
        },
      },
      tabs: {
        include: {
          visualizations: true,
        },
      },
    },
    orderBy: {
      updated_at: "desc",
    },
  })

  const userIsAdmin = isAdmin(session.user.roles || [])

  return (
    <DashboardLayout user={session.user}>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">My Dashboards</h2>
            <p className="text-muted-foreground">
              View and manage your dashboards
            </p>
          </div>
          {userIsAdmin && (
            <Link href="/dashboard/my-dashboards/create">
              <Button className="flex items-center space-x-2">
                <Plus className="h-4 w-4" />
                <span>Create Dashboard</span>
              </Button>
            </Link>
          )}
        </div>

        {/* Stats */}
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Dashboards
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboards.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                My Dashboards
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {dashboards.filter((d) => d.created_by === session.user.id).length}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Shared With Me
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {dashboards.filter((d) => d.created_by !== session.user.id).length}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Dashboards Grid */}
        {dashboards.length > 0 ? (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {dashboards.map((dashboard) => {
              const visualizationsCount = dashboard.tabs.reduce(
                (acc, tab) => acc + tab.visualizations.length,
                0
              )

              return (
                <Card key={dashboard.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3">
                        <div className="rounded-lg bg-primary/10 p-2">
                          <BarChart3 className="h-5 w-5 text-primary" />
                        </div>
                        <div className="space-y-1">
                          <CardTitle className="text-lg">{dashboard.name}</CardTitle>
                          <CardDescription className="line-clamp-2">
                            {dashboard.description || "No description"}
                          </CardDescription>
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">
                        {dashboard.tabs.length} tabs • {visualizationsCount} charts
                      </span>
                      {dashboard.created_by === session.user.id && (
                        <Badge variant="secondary">Owner</Badge>
                      )}
                    </div>

                    <div className="text-xs text-muted-foreground">
                      <p>Created by {dashboard.creator?.full_name || "Unknown"}</p>
                      <p>Updated {formatDateTime(dashboard.updated_at)}</p>
                    </div>

                    <div className="flex items-center space-x-2 pt-2">
                      <Link href={`/dashboard/my-dashboards/${dashboard.id}`} className="flex-1">
                        <Button variant="default" size="sm" className="w-full">
                          <Eye className="h-4 w-4 mr-2" />
                          View
                        </Button>
                      </Link>
                      {(userIsAdmin || dashboard.created_by === session.user.id) && (
                        <Button variant="outline" size="sm">
                          <Edit className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        ) : (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <BarChart3 className="h-16 w-16 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No dashboards yet</h3>
              <p className="text-sm text-muted-foreground mb-4 text-center max-w-md">
                Get started by creating your first dashboard or wait for others to share with you.
              </p>
              {userIsAdmin && (
                <Link href="/dashboard/my-dashboards/create">
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Your First Dashboard
                  </Button>
                </Link>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  )
}
