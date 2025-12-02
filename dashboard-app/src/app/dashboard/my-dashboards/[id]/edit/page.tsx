import { auth } from "@/auth"
import { redirect } from "next/navigation"
import { prisma } from "@/lib/prisma"
import { DashboardCanvas } from "@/components/DashboardCanvas"
import { Button } from "@/components/ui/Button"
import Link from "next/link"
import { ArrowLeft, Plus } from "lucide-react"

export default async function EditDashboardPage({
  params,
}: {
  params: { id: string }
}) {
  const session = await auth()
  if (!session?.user?.id) {
    redirect("/auth/signin")
  }

  const dashboardId = parseInt(params.id)
  const dashboard = await prisma.dashboard.findUnique({
    where: { id: dashboardId },
    include: {
      tabs: {
        include: { visualizations: true },
        orderBy: { order: "asc" },
      },
    },
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

  // Only creator can edit
  const isCreator = dashboard.created_by === session.user.id
  if (!isCreator) {
    redirect(`/dashboard/viewer/${params.id}`)
  }

  const activeTab = dashboard.tabs[0]

  async function addTab() {
    "use server"

    const maxOrder = await prisma.dashboardTab.findFirst({
      where: { dashboard_id: dashboardId },
      orderBy: { order: "desc" },
      select: { order: true },
    })

    await prisma.dashboardTab.create({
      data: {
        dashboard_id: dashboardId,
        name: `Tab ${(maxOrder?.order || 0) + 1}`,
        order: (maxOrder?.order || 0) + 1,
      },
    })
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-6">
        <div className="max-w-7xl mx-auto flex justify-between items-start">
          <div>
            <Link
              href="/dashboard/my-dashboards"
              className="inline-flex items-center text-blue-600 hover:text-blue-800 mb-3"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Link>

            <h1 className="text-3xl font-bold text-gray-900">
              {dashboard.name}
            </h1>
            <p className="text-gray-600 mt-1">{dashboard.description}</p>
          </div>

          <div className="flex gap-2">
            <Link href={`/dashboard/viewer/${dashboard.id}`}>
              <Button variant="secondary">Preview</Button>
            </Link>
            <Link href="/dashboard/my-dashboards">
              <Button>Done</Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Tabs Bar */}
      {dashboard.tabs.length > 0 && (
        <div className="bg-white border-b border-gray-200 px-6">
          <div className="max-w-7xl mx-auto flex items-center gap-6">
            {dashboard.tabs.map((tab) => (
              <button
                key={tab.id}
                className={`px-1 py-4 font-medium border-b-2 transition-colors ${
                  tab.id === activeTab.id
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-600 hover:text-gray-900"
                }`}
              >
                {tab.name}
              </button>
            ))}

            <form action={addTab}>
              <Button type="submit" variant="ghost" size="sm">
                <Plus className="h-4 w-4 mr-1" />
                Add Tab
              </Button>
            </form>
          </div>
        </div>
      )}

      {/* Canvas */}
      {activeTab && (
        <div className="flex-1 overflow-hidden bg-gray-50 p-6">
          <div className="max-w-7xl mx-auto h-full">
            <DashboardCanvas
              tabId={activeTab.id}
              dashboardId={dashboard.id}
              isCreator={isCreator}
            />
          </div>
        </div>
      )}
    </div>
  )
}
