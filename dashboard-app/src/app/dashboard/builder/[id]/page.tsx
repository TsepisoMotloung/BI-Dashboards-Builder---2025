import { auth } from "@/auth"
import { redirect } from "next/navigation"
import { prisma } from "@/lib/prisma"
import { DashboardCanvas } from "@/components/DashboardCanvas"
import { Button } from "@/components/ui/Button"
import Link from "next/link"
import PublishDashboardButton from "@/components/PublishDashboardButton"

export default async function DashboardBuilderPage({
  params,
}: {
  params: { id: string }
}) {
  const session = await auth()
  if (!session?.user?.id) {
    redirect("/auth/signin")
  }

  const dashboard = await prisma.dashboard.findUnique({
    where: { id: parseInt(params.id) },
    include: { tabs: { include: { visualizations: true } } },
  })

  if (!dashboard) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Dashboard not found</h1>
        <Link href="/dashboard/my-dashboards">
          <Button>Back to My Dashboards</Button>
        </Link>
      </div>
    )
  }

  // Only creator can build
  const isCreator = dashboard.created_by === session.user.id
  if (!isCreator) {
    redirect(`/dashboard/viewer/${params.id}`)
  }

  const defaultTab = dashboard.tabs[0]

  // Prepare initial visualizations for client component
  const initialVisualizations = defaultTab.visualizations.map((v: any) => {
    let config: any = {}
    try {
      config = typeof v.config === "string" ? JSON.parse(v.config || "{}") : v.config || {}
    } catch (e) {
      config = {}
    }

    const cfg: any = config

    return {
      id: v.id,
      type: v.type,
      config: cfg,
      query: v.query,
      order: v.order,
      x: (cfg && cfg.__layout && cfg.__layout.x) ?? cfg.x ?? 0,
      y: (cfg && cfg.__layout && cfg.__layout.y) ?? cfg.y ?? 0,
      width: (cfg && cfg.__layout && cfg.__layout.width) ?? cfg.width ?? 400,
      height: (cfg && cfg.__layout && cfg.__layout.height) ?? cfg.height ?? 300,
    }
  })

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Header */}
      <div className="border-b border-gray-200 p-4 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{dashboard.name}</h1>
          <p className="text-sm text-gray-500 mt-1">
            {dashboard.description}
          </p>
        </div>

        <div className="flex gap-3 items-center">
          <PublishDashboardButton
            dashboardId={dashboard.id}
            initialPublished={dashboard.is_published}
          />
          <Link href="/dashboard/my-dashboards">
            <Button variant="secondary">Done Editing</Button>
          </Link>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 px-4 flex gap-4 bg-gray-50">
        {dashboard.tabs.map((tab) => (
          <button
            key={tab.id}
            className={`px-4 py-3 font-medium border-b-2 transition-colors ${
              tab.id === defaultTab.id
                ? "border-blue-500 text-blue-600 bg-white"
                : "border-transparent text-gray-600 hover:text-gray-900"
            }`}
          >
            {tab.name}
          </button>
        ))}
      </div>

      {/* Canvas Area */}
      {defaultTab && (
        <div className="flex-1 overflow-hidden">
          <DashboardCanvas
            tabId={defaultTab.id}
            dashboardId={dashboard.id}
            isCreator={isCreator}
            initialVisualizations={initialVisualizations}
          />
        </div>
      )}
    </div>
  )
}
