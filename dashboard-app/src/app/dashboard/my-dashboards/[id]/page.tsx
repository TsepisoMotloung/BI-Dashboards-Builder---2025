import { auth } from "@/auth"
import { redirect, notFound } from "next/navigation"
import { DashboardLayout } from "@/components/layout/DashboardLayout"
import { Card, CardContent } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { prisma } from "@/lib/prisma"
import { BarChart } from "@/components/charts/BarChart"
import { LineChart } from "@/components/charts/LineChart"
import { PieChart } from "@/components/charts/PieChart"
import { RefreshCw, Edit } from "lucide-react"
import { ExportButton } from "@/components/dashboard/ExportButton"
import { Button } from "@/components/ui/Button"

interface DashboardViewPageProps {
  params: {
    id: string
  }
}

export default async function DashboardViewPage({ params }: DashboardViewPageProps) {
  const session = await auth()

  if (!session) {
    redirect("/auth/signin")
  }

  const dashboardId = parseInt(params.id)

  if (isNaN(dashboardId)) {
    notFound()
  }

  const dashboard = await prisma.dashboard.findUnique({
    where: { id: dashboardId },
    include: {
      tabs: {
        include: {
          visualizations: true,
        },
        orderBy: {
          order: "asc",
        },
      },
      creator: {
        select: {
          full_name: true,
        },
      },
    },
  })

  if (!dashboard) {
    notFound()
  }

  return (
    <DashboardLayout user={session.user}>
      <div className="space-y-6" id="dashboard-content">
        {/* Dashboard Header */}
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">{dashboard.name}</h2>
            {dashboard.description && (
              <p className="text-muted-foreground mt-1">{dashboard.description}</p>
            )}
            <div className="flex items-center space-x-2 mt-2">
              <Badge variant="secondary">
                Created by {dashboard.creator?.full_name || "Unknown"}
              </Badge>
              <Badge variant="outline">
                {dashboard.tabs.length} tabs
              </Badge>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
            <ExportButton
              elementId="dashboard-content"
              dashboardName={dashboard.name}
              variant="outline"
              size="sm"
            />
            {dashboard.created_by === session.user.id && (
              <Button variant="default" size="sm">
                <Edit className="h-4 w-4 mr-2" />
                Edit
              </Button>
            )}
          </div>
        </div>

        {/* Dashboard Content */}
        {dashboard.tabs.length > 0 ? (
          <DashboardTabs tabs={dashboard.tabs} />
        ) : (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <p className="text-muted-foreground">
                This dashboard has no visualizations yet.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  )
}

function DashboardTabs({ tabs }: { tabs: any[] }) {
  // For now, show first tab (in production, implement tab switching)
  const activeTab = tabs[0]

  if (!activeTab) return null

  return (
    <div className="space-y-4">
      {/* Tab Navigation (simplified for now) */}
      {tabs.length > 1 && (
        <div className="flex space-x-2 border-b">
          {tabs.map((tab, index) => (
            <button
              key={tab.id}
              className={`px-4 py-2 text-sm font-medium transition-colors ${
                index === 0
                  ? "border-b-2 border-primary text-primary"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {tab.name}
            </button>
          ))}
        </div>
      )}

      {/* Visualizations Grid */}
      {activeTab.visualizations.length > 0 ? (
        <div className="grid gap-6 md:grid-cols-2">
          {activeTab.visualizations.map((viz: any) => (
            <VisualizationCard key={viz.id} visualization={viz} />
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="py-8 text-center text-muted-foreground">
            No visualizations in this tab yet.
          </CardContent>
        </Card>
      )}
    </div>
  )
}

function VisualizationCard({ visualization }: { visualization: any }) {
  const config = JSON.parse(visualization.config)

  // Generate sample data for demonstration
  const sampleData = generateSampleData(visualization.type)

  return (
    <Card>
      <CardContent className="p-6">
        {visualization.type === "bar" && (
          <BarChart
            data={sampleData}
            title={config.title || "Bar Chart"}
            xAxisTitle={config.xAxisTitle}
            yAxisTitle={config.yAxisTitle}
            height={350}
          />
        )}
        {visualization.type === "line" && (
          <LineChart
            data={sampleData}
            title={config.title || "Line Chart"}
            xAxisTitle={config.xAxisTitle}
            yAxisTitle={config.yAxisTitle}
            height={350}
          />
        )}
        {visualization.type === "pie" && (
          <PieChart
            data={sampleData}
            title={config.title || "Pie Chart"}
            height={350}
          />
        )}
      </CardContent>
    </Card>
  )
}

// Helper function to generate sample data
function generateSampleData(type: string) {
  if (type === "bar" || type === "line") {
    return [
      {
        x: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        y: [65, 59, 80, 81, 56, 55],
        name: "Sales",
        color: "#3B82F6",
      },
    ]
  }

  if (type === "pie") {
    return {
      labels: ["Product A", "Product B", "Product C", "Product D"],
      values: [30, 25, 25, 20],
    }
  }

  return []
}
