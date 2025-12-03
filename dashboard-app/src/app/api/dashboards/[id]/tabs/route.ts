import { auth } from "@/auth"
import { prisma } from "@/lib/prisma"
import { getUserId } from "@/lib/auth-utils"
import { NextRequest, NextResponse } from "next/server"

/**
 * POST /api/dashboards/[id]/tabs
 * Create a new tab in a dashboard
 */
export async function POST(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const session = await auth()
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }
    const userId = getUserId(session.user.id)
    const dashboardId = parseInt(params.id)
    if (isNaN(dashboardId)) {
      return NextResponse.json({ error: "Invalid dashboard id" }, { status: 400 })
    }

    const dashboard = await prisma.dashboard.findUnique({ where: { id: dashboardId } })
    if (!dashboard || dashboard.created_by !== userId) {
      return NextResponse.json({ error: "Access denied" }, { status: 403 })
    }

    const body = await req.json()
    const name = typeof body.name === "string" ? body.name.trim() : undefined
    const order = body.order !== undefined ? parseInt(body.order) : undefined

    if (name !== undefined && (name.length === 0 || name.length > 255)) {
      return NextResponse.json({ error: "Invalid tab name" }, { status: 400 })
    }

    // Get max order
    const maxOrder = await prisma.dashboardTab.findFirst({
      where: { dashboard_id: dashboardId },
      orderBy: { order: "desc" },
      select: { order: true },
    })

    const tab = await prisma.dashboardTab.create({
      data: {
        dashboard_id: dashboardId,
        name: name || `Tab ${(maxOrder?.order || 0) + 1}`,
        order: Number.isInteger(order) ? order : (maxOrder?.order || 0) + 1,
      },
    })

    return NextResponse.json(tab, { status: 201 })
  } catch (error) {
    console.error("Error creating tab:", error)
    return NextResponse.json(
      { error: "Failed to create tab" },
      { status: 500 }
    )
  }
}
