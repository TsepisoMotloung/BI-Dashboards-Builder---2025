import { auth } from "@/auth"
import { redirect } from "next/navigation"
import { DashboardLayout } from "@/components/layout/DashboardLayout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Button } from "@/components/ui/Button"
import { prisma } from "@/lib/prisma"
import { formatDateTime } from "@/lib/utils"
import { Database, Plus, Eye } from "lucide-react"

export default async function DataModelsPage() {
  const session = await auth()

  if (!session) {
    redirect("/auth/signin")
  }

  const dataModels = await prisma.dataModel.findMany({
    include: {
      upload_history: {
        select: { id: true },
      },
    },
    orderBy: {
      created_at: "desc",
    },
  })

  return (
    <DashboardLayout user={session.user}>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Data Models</h2>
            <p className="text-muted-foreground">
              Manage your data structures and schemas
            </p>
          </div>
          <Button className="flex items-center space-x-2">
            <Plus className="h-4 w-4" />
            <span>New Model</span>
          </Button>
        </div>

        {/* Summary Stats */}
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Models
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dataModels.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Uploads
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {dataModels.reduce((acc, dm) => acc + dm.upload_history.length, 0)}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Latest Version
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                v{Math.max(...dataModels.map((dm) => dm.version), 0)}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Data Models List */}
        <Card>
          <CardHeader>
            <CardTitle>Available Data Models</CardTitle>
            <CardDescription>
              Browse and manage your data model definitions
            </CardDescription>
          </CardHeader>
          <CardContent>
            {dataModels.length > 0 ? (
              <div className="space-y-4">
                {dataModels.map((model) => {
                  const schema = JSON.parse(model.schema_json)
                  const fieldsCount = schema.fields?.length || 0

                  return (
                    <div
                      key={model.id}
                      className="flex items-start justify-between rounded-lg border p-4 hover:bg-accent/50 transition-colors"
                    >
                      <div className="flex items-start space-x-4">
                        <div className="rounded-lg bg-primary/10 p-3">
                          <Database className="h-6 w-6 text-primary" />
                        </div>
                        <div className="space-y-1">
                          <div className="flex items-center space-x-2">
                            <h3 className="font-semibold">{model.name}</h3>
                            <Badge variant="secondary">v{model.version}</Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {fieldsCount} fields • {model.upload_history.length} uploads
                          </p>
                          <p className="text-xs text-muted-foreground">
                            Created {formatDateTime(model.created_at)}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4 mr-2" />
                          View
                        </Button>
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              <div className="text-center py-12">
                <Database className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No data models yet</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Create your first data model to start organizing your data
                </p>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Create Model
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
