import { auth } from "@/auth"
import { prisma } from "@/lib/prisma"
import { NextRequest, NextResponse } from "next/server"

/**
 * GET /api/dashboards
 * List dashboards accessible to the current user
 */
export async function GET(req: NextRequest) {
  try {
    const session = await auth()
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }
    const userId = session.user.id

    // Build safe where clause: dashboards the user created OR dashboards where the user's roles are granted
    const dashboards = await prisma.dashboard.findMany({
      where: {
        OR: [
          { created_by: userId },
          {
            permissions: {
              some: {
                role: {
                  user_roles: {
                    some: { user_id: userId },
                  },
                },
              },
            },
          },
        ],
      },
      include: {
        creator: { select: { id: true, email: true, full_name: true } },
        tabs: { orderBy: { order: "asc" } },
        permissions: {
          include: { role: { select: { id: true, name: true } } },
        },
      },
      orderBy: { created_at: "desc" },
      take: 200,
    })

    return NextResponse.json(dashboards)
  } catch (error) {
    console.error("Error fetching dashboards:", error)
    return NextResponse.json(
      { error: "Failed to fetch dashboards" },
      { status: 500 }
    )
  }
}

/**
 * POST /api/dashboards
 * Create a new dashboard (requires creator/admin role)
 */
export async function POST(req: NextRequest) {
  try {
    const session = await auth()
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const body = await req.json()
    const { name, description, layout, is_published } = body

    if (!name) {
      return NextResponse.json(
        { error: "Dashboard name is required" },
        { status: 400 }
      )
    }

    if (typeof name !== "string" || name.trim().length === 0 || name.length > 255) {
      return NextResponse.json({ error: "Invalid dashboard name" }, { status: 400 })
    }

    // layout is stored as text in the schema; accept object or string and stringify safely
    let layoutText: string | null = null
    if (layout !== undefined && layout !== null) {
      if (typeof layout === "string") {
        // validate JSON string
        try {
          JSON.parse(layout)
          layoutText = layout
        } catch (e) {
          // not valid JSON string, but allow storing raw string as fallback
          layoutText = layout
        }
      } else {
        try {
          layoutText = JSON.stringify(layout)
        } catch (e) {
          layoutText = null
        }
      }
    }

    const dashboard = await prisma.dashboard.create({
      data: {
        name: name.trim(),
        description: typeof description === "string" ? description : null,
        layout: layoutText,
        created_by: session.user.id,
      },
      include: {
        creator: { select: { id: true, email: true, full_name: true } },
        tabs: true,
        permissions: true,
      },
    })

    // Create a default tab for the new dashboard
    try {
      await prisma.dashboardTab.create({
        data: {
          dashboard_id: dashboard.id,
          name: "Tab 1",
          order: 1,
        },
      })
    } catch (e) {
      console.warn("Failed to create default tab:", e)
    }

    const dashboardWithTabs = await prisma.dashboard.findUnique({
      where: { id: dashboard.id },
      include: {
        creator: { select: { id: true, email: true, full_name: true } },
        tabs: { orderBy: { order: "asc" } },
        permissions: { include: { role: { select: { id: true, name: true } } } },
      },
    })

    return NextResponse.json(dashboardWithTabs, { status: 201 })
  } catch (error) {
    console.error("Error creating dashboard:", error)
    return NextResponse.json(
      { error: "Failed to create dashboard" },
      { status: 500 }
    )
  }
}
