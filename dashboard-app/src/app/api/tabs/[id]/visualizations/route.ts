import { auth } from "@/auth"
import { prisma } from "@/lib/prisma"
import { NextRequest, NextResponse } from "next/server"

/**
 * POST /api/tabs/[id]/visualizations
 * Create a visualization in a tab
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

    const tab = await prisma.dashboardTab.findUnique({
        where: { id: parseInt(params.id) },
      include: { dashboard: true },
    })

    if (!tab || tab.dashboard.created_by !== session.user.id) {
      return NextResponse.json(
        { error: "Access denied" },
        { status: 403 }
      )
    }

    const body = await req.json()
    const { type, config, query } = body

    if (!type || typeof type !== "string" || type.length > 50) {
      return NextResponse.json({ error: "Invalid visualization type" }, { status: 400 })
    }

    // Get max order
    const tabId = parseInt(params.id)
    const maxOrder = await prisma.visualization.findFirst({
      where: { tab_id: tabId },
      orderBy: { order: "desc" },
      select: { order: true },
    })

    const visualization = await prisma.visualization.create({
      data: {
        tab_id: tabId,
        type: type.trim(),
        config: JSON.stringify(config || {}),
        query: query || null,
        order: (maxOrder?.order || 0) + 1,
      },
    })

    return NextResponse.json(visualization, { status: 201 })
  } catch (error) {
    console.error("Error creating visualization:", error)
    return NextResponse.json(
      { error: "Failed to create visualization" },
      { status: 500 }
    )
  }
}

/**
 * PUT /api/tabs/[id]/visualizations/[vis_id]
 * Update a visualization
 */
export async function PUT(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const session = await auth()
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const url = new URL(req.url)
    const vis_id = parseInt(url.searchParams.get("vis_id") || "")
    if (isNaN(vis_id)) {
      return NextResponse.json({ error: "vis_id is required" }, { status: 400 })
    }

    const visualization = await prisma.visualization.findUnique({
      where: { id: vis_id },
      include: { tab: { include: { dashboard: true } } },
    })

    if (!visualization || visualization.tab.dashboard.created_by !== session.user.id) {
      return NextResponse.json({ error: "Access denied" }, { status: 403 })
    }

    const body = await req.json()
    const updateData: any = {}
    if (body.type !== undefined) {
      if (typeof body.type !== "string" || body.type.length === 0 || body.type.length > 50) {
        return NextResponse.json({ error: "Invalid visualization type" }, { status: 400 })
      }
      updateData.type = body.type.trim()
    }

    if (body.config !== undefined) {
      try {
        updateData.config = JSON.stringify(body.config)
      } catch (e) {
        return NextResponse.json({ error: "Invalid config" }, { status: 400 })
      }
    }

    if (body.query !== undefined) {
      updateData.query = body.query
    }

    const updated = await prisma.visualization.update({ where: { id: vis_id }, data: updateData })

    return NextResponse.json(updated)
  } catch (error) {
    console.error("Error updating visualization:", error)
    return NextResponse.json(
      { error: "Failed to update visualization" },
      { status: 500 }
    )
  }
}

/**
 * DELETE /api/tabs/[id]/visualizations/[vis_id]
 * Delete a visualization
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

    const url = new URL(req.url)
    const vis_id = parseInt(url.searchParams.get("vis_id") || "")
    if (isNaN(vis_id)) {
      return NextResponse.json({ error: "vis_id is required" }, { status: 400 })
    }

    const visualization = await prisma.visualization.findUnique({
      where: { id: vis_id },
      include: { tab: { include: { dashboard: true } } },
    })

    if (!visualization || visualization.tab.dashboard.created_by !== session.user.id) {
      return NextResponse.json({ error: "Access denied" }, { status: 403 })
    }

    await prisma.visualization.delete({ where: { id: vis_id } })

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error("Error deleting visualization:", error)
    return NextResponse.json(
      { error: "Failed to delete visualization" },
      { status: 500 }
    )
  }
}
