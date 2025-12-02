import { auth } from "@/auth"
import { prisma } from "@/lib/prisma"
import { NextRequest, NextResponse } from "next/server"

interface DashboardParams {
  params: { id: string }
}

/**
 * GET /api/dashboards/[id]
 * Get a specific dashboard (with access control)
 */
export async function GET(req: NextRequest, { params }: DashboardParams) {
  try {
    const session = await auth()
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }
    const dashboardId = parseInt(params.id)
    if (isNaN(dashboardId)) {
      return NextResponse.json({ error: "Invalid dashboard id" }, { status: 400 })
    }

    const dashboard = await prisma.dashboard.findUnique({
      where: { id: dashboardId },
      include: {
        creator: { select: { id: true, email: true, full_name: true } },
        tabs: {
          orderBy: { order: "asc" },
          include: {
            visualizations: { orderBy: { order: "asc" } },
          },
        },
        permissions: {
          include: { role: { select: { id: true, name: true } } },
        },
      },
    })

    if (!dashboard) {
      return NextResponse.json(
        { error: "Dashboard not found" },
        { status: 404 }
      )
    }

    // Check access: creator or has role with permission
    const hasAccess =
      dashboard.created_by === session.user.id ||
      (await prisma.dashboardPermission.findFirst({
        where: {
          dashboard_id: dashboard.id,
          role: {
            user_roles: { some: { user_id: session.user.id } },
          },
        },
      }))

    if (!hasAccess) {
      return NextResponse.json(
        { error: "Access denied to this dashboard" },
        { status: 403 }
      )
    }

    return NextResponse.json(dashboard)
  } catch (error) {
    console.error("Error fetching dashboard:", error)
    return NextResponse.json(
      { error: "Failed to fetch dashboard" },
      { status: 500 }
    )
  }
}

/**
 * PUT /api/dashboards/[id]
 * Update a dashboard (only creator or admin)
 */
export async function PUT(req: NextRequest, { params }: DashboardParams) {
  try {
    const session = await auth()
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }
    const dashboardId = parseInt(params.id)
    if (isNaN(dashboardId)) {
      return NextResponse.json({ error: "Invalid dashboard id" }, { status: 400 })
    }

    const dashboard = await prisma.dashboard.findUnique({
      where: { id: dashboardId },
    })

    if (!dashboard) {
      return NextResponse.json({ error: "Dashboard not found" }, { status: 404 })
    }

    // Only creator or admin can update
    if (dashboard.created_by !== session.user.id) {
      return NextResponse.json(
        { error: "Only dashboard creator can update" },
        { status: 403 }
      )
    }

    const body = await req.json()

    const updates: any = {}
    if (body.name !== undefined) {
      if (typeof body.name !== "string" || body.name.trim().length === 0 || body.name.length > 255) {
        return NextResponse.json({ error: "Invalid dashboard name" }, { status: 400 })
      }
      updates.name = body.name.trim()
    }

    if (body.description !== undefined) {
      updates.description = typeof body.description === "string" ? body.description : null
    }

    if (body.layout !== undefined) {
      try {
        updates.layout = typeof body.layout === "string" ? body.layout : JSON.stringify(body.layout)
      } catch (e) {
        return NextResponse.json({ error: "Invalid layout format" }, { status: 400 })
      }
    }

    const updated = await prisma.dashboard.update({
      where: { id: dashboardId },
      data: updates,
      include: {
        creator: { select: { id: true, email: true, full_name: true } },
        tabs: { orderBy: { order: "asc" } },
        permissions: true,
      },
    })

    return NextResponse.json(updated)
  } catch (error) {
    console.error("Error updating dashboard:", error)
    return NextResponse.json(
      { error: "Failed to update dashboard" },
      { status: 500 }
    )
  }
}

/**
 * DELETE /api/dashboards/[id]
 * Delete a dashboard (only creator or admin)
 */
export async function DELETE(req: NextRequest, { params }: DashboardParams) {
  try {
    const session = await auth()
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }
    const dashboardId = parseInt(params.id)
    if (isNaN(dashboardId)) {
      return NextResponse.json({ error: "Invalid dashboard id" }, { status: 400 })
    }

    const dashboard = await prisma.dashboard.findUnique({ where: { id: dashboardId } })
    if (!dashboard) {
      return NextResponse.json({ error: "Dashboard not found" }, { status: 404 })
    }

    if (dashboard.created_by !== session.user.id) {
      return NextResponse.json({ error: "Only dashboard creator can delete" }, { status: 403 })
    }

    await prisma.dashboard.delete({ where: { id: dashboardId } })

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error("Error deleting dashboard:", error)
    return NextResponse.json(
      { error: "Failed to delete dashboard" },
      { status: 500 }
    )
  }
}
