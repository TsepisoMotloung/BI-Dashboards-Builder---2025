import { auth } from "@/auth"
import { redirect } from "next/navigation"
import { prisma } from "@/lib/prisma"
import { getUserId } from "@/lib/auth-utils"
import { DashboardLayout } from "@/components/layout/DashboardLayout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import Link from "next/link"

async function createDashboard(formData: FormData) {
  "use server"

  const session = await auth()
  if (!session?.user?.id) {
    return redirect("/auth/signin")
  }

  const userId = getUserId(session.user.id)
  const name = formData.get("name") as string
  const description = formData.get("description") as string

  if (!name) {
    // In a real app, we'd handle this better with form state
    return redirect("/dashboard/my-dashboards")
  }

  try {
    const dashboard = await prisma.dashboard.create({
      data: {
        name,
        description: description || "",
        created_by: userId,
      },
    })

    // Create default tab
    await prisma.dashboardTab.create({
      data: {
        dashboard_id: dashboard.id,
        name: "Tab 1",
        order: 1,
      },
    })

    redirect(`/dashboard/builder/${dashboard.id}`)
  } catch (error) {
    console.error("Error creating dashboard:", error)
    return redirect("/dashboard/my-dashboards")
  }
}

export default async function CreateDashboardPage() {
  const session = await auth()
  if (!session?.user?.id) {
    redirect("/auth/signin")
  }

  return (
    <DashboardLayout user={session.user}>
      <div className="max-w-2xl mx-auto py-8">
        <div className="mb-8">
          <Link href="/dashboard/my-dashboards">
            <Button variant="ghost" className="mb-4">
              ← Back
            </Button>
          </Link>

          <h1 className="text-3xl font-bold tracking-tight">Create Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Create a new dashboard to start building visualizations
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Dashboard Details</CardTitle>
            <CardDescription>
              Provide a name and description for your dashboard
            </CardDescription>
          </CardHeader>

          <CardContent>
            <form action={createDashboard} className="space-y-4">
              <div>
                <label
                  htmlFor="name"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Dashboard Name *
                </label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  required
                  placeholder="e.g., Sales Performance"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label
                  htmlFor="description"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Description
                </label>
                <textarea
                  id="description"
                  name="description"
                  placeholder="Describe what this dashboard shows..."
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex gap-2 pt-4">
                <Button type="submit" variant="default">
                  Create Dashboard
                </Button>

                <Link href="/dashboard/my-dashboards">
                  <Button type="button" variant="secondary">
                    Cancel
                  </Button>
                </Link>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
