import { auth } from "@/auth"
import { prisma } from "@/lib/prisma"
import { NextRequest, NextResponse } from "next/server"

/**
 * POST /api/dashboards/[id]/publish
 * Publish a dashboard (creator-only)
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

    if (dashboard.created_by !== session.user.id) {
      return NextResponse.json(
        { error: "Only dashboard creator can publish" },
        { status: 403 }
      )
    }

    const updated = await prisma.dashboard.update({
      where: { id: dashboardId },
      data: { is_published: true },
      include: {
        creator: { select: { id: true, email: true, full_name: true } },
        tabs: { orderBy: { order: "asc" } },
        permissions: { include: { role: { select: { id: true, name: true } } } },
      },
    })

    return NextResponse.json(updated)
  } catch (error) {
    console.error("Error publishing dashboard:", error)
    return NextResponse.json(
      { error: "Failed to publish dashboard" },
      { status: 500 }
    )
  }
}

/**
 * DELETE /api/dashboards/[id]/publish
 * Unpublish a dashboard (creator-only)
 */
export async function DELETE(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
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

    if (dashboard.created_by !== session.user.id) {
      return NextResponse.json(
        { error: "Only dashboard creator can unpublish" },
        { status: 403 }
      )
    }

    const updated = await prisma.dashboard.update({
      where: { id: dashboardId },
      data: { is_published: false },
      include: {
        creator: { select: { id: true, email: true, full_name: true } },
        tabs: { orderBy: { order: "asc" } },
        permissions: { include: { role: { select: { id: true, name: true } } } },
      },
    })

    return NextResponse.json(updated)
  } catch (error) {
    console.error("Error unpublishing dashboard:", error)
    return NextResponse.json(
      { error: "Failed to unpublish dashboard" },
      { status: 500 }
    )
  }
}
