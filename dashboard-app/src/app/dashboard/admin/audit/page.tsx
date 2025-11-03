import { auth } from "@/auth"
import { redirect } from "next/navigation"
import { DashboardLayout } from "@/components/layout/DashboardLayout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { prisma } from "@/lib/prisma"
import { formatDateTime, isAdmin } from "@/lib/utils"
import { Activity, User, Database, Upload, Settings } from "lucide-react"

export default async function AuditLogsPage() {
  const session = await auth()

  if (!session || !isAdmin(session.user.roles || [])) {
    redirect("/dashboard")
  }

  // Get audit logs
  const logs = await prisma.auditLog.findMany({
    include: {
      user: {
        select: {
          full_name: true,
          email: true,
        },
      },
    },
    orderBy: {
      created_at: "desc",
    },
    take: 100,
  })

  // Get statistics
  const stats = {
    total: logs.length,
    users: new Set(logs.map((l) => l.user_id).filter(Boolean)).size,
    actions: new Set(logs.map((l) => l.action)).size,
    resources: new Set(logs.map((l) => l.resource)).size,
  }

  return (
    <DashboardLayout user={session.user}>
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Audit Logs</h2>
          <p className="text-muted-foreground">
            System activity and security audit trail
          </p>
        </div>

        {/* Stats */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Events
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Active Users
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.users}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Action Types
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.actions}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Resources
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.resources}</div>
            </CardContent>
          </Card>
        </div>

        {/* Audit Logs Table */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>
              Last 100 system events and user actions
            </CardDescription>
          </CardHeader>
          <CardContent>
            {logs.length > 0 ? (
              <div className="space-y-2">
                {logs.map((log) => (
                  <div
                    key={log.id}
                    className="flex items-start justify-between rounded-lg border p-4 hover:bg-accent/50 transition-colors"
                  >
                    <div className="flex items-start space-x-3">
                      <div className="rounded-lg bg-primary/10 p-2">
                        {getActionIcon(log.resource)}
                      </div>
                      <div className="space-y-1">
                        <div className="flex items-center space-x-2">
                          <p className="font-medium">{log.action}</p>
                          <Badge variant="outline">{log.resource}</Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          by {log.user?.full_name || "System"} ({log.user?.email || "system"})
                        </p>
                        {log.details && (
                          <p className="text-xs text-muted-foreground">
                            Details: {log.details}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium">
                        {formatDateTime(log.created_at)}
                      </p>
                      {log.ip_address && (
                        <p className="text-xs text-muted-foreground">
                          IP: {log.ip_address}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <Activity className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No audit logs yet</h3>
                <p className="text-sm text-muted-foreground">
                  Activity will appear here as users interact with the system
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}

function getActionIcon(resource: string) {
  const iconClass = "h-5 w-5 text-primary"
  
  switch (resource.toLowerCase()) {
    case "users":
      return <User className={iconClass} />
    case "data_models":
      return <Database className={iconClass} />
    case "uploads":
      return <Upload className={iconClass} />
    case "settings":
      return <Settings className={iconClass} />
    default:
      return <Activity className={iconClass} />
  }
}
