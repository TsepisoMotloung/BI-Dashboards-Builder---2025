import { auth } from "@/auth"
import { prisma } from "@/lib/prisma"
import { getUserId } from "@/lib/auth-utils"
import { NextRequest, NextResponse } from "next/server"

/**
 * POST /api/dashboards/[id]/permissions
 * Grant role access to a dashboard (admin only)
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

    if (!dashboard) {
      return NextResponse.json(
        { error: "Dashboard not found" },
        { status: 404 }
      )
    }

    // Only creator can manage permissions
    if (dashboard.created_by !== userId) {
      return NextResponse.json(
        { error: "Only dashboard creator can manage permissions" },
        { status: 403 }
      )
    }

    const body = await req.json()
    const { role_id, permissions } = body

    const roleId = parseInt(role_id)
    if (isNaN(roleId)) {
      return NextResponse.json({ error: "Invalid role_id" }, { status: 400 })
    }

    // ensure role exists
    const role = await prisma.role.findUnique({ where: { id: roleId } })
    if (!role) {
      return NextResponse.json({ error: "Role not found" }, { status: 404 })
    }

    let permissionsJson = JSON.stringify(permissions || { view: true })
    try {
      // validate JSON can be parsed
      JSON.parse(permissionsJson)
    } catch (e) {
      return NextResponse.json({ error: "Invalid permissions JSON" }, { status: 400 })
    }

    const permission = await prisma.dashboardPermission.upsert({
      where: {
        dashboard_id_role_id: {
          dashboard_id: dashboardId,
          role_id: roleId,
        },
      },
      update: {
        permissions_json: permissionsJson,
      },
      create: {
        dashboard_id: dashboardId,
        role_id: roleId,
        permissions_json: permissionsJson,
      },
      include: {
        role: { select: { id: true, name: true } },
      },
    })

    return NextResponse.json(permission, { status: 201 })
  } catch (error) {
    console.error("Error setting dashboard permission:", error)
    return NextResponse.json(
      { error: "Failed to set permission" },
      { status: 500 }
    )
  }
}

/**
 * DELETE /api/dashboards/[id]/permissions/[role_id]
 * Revoke role access to a dashboard
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
    const userId = getUserId(session.user.id)
    const dashboardId = parseInt(params.id)
    if (isNaN(dashboardId)) {
      return NextResponse.json({ error: "Invalid dashboard id" }, { status: 400 })
    }

    const dashboard = await prisma.dashboard.findUnique({ where: { id: dashboardId } })
    if (!dashboard) {
      return NextResponse.json({ error: "Dashboard not found" }, { status: 404 })
    }

    if (dashboard.created_by !== userId) {
      return NextResponse.json({ error: "Only dashboard creator can manage permissions" }, { status: 403 })
    }

    const url = new URL(req.url)
    const roleId = parseInt(url.searchParams.get("role_id") || "")
    if (isNaN(roleId)) {
      return NextResponse.json({ error: "role_id is required" }, { status: 400 })
    }

    await prisma.dashboardPermission.delete({
      where: {
        dashboard_id_role_id: {
          dashboard_id: dashboardId,
          role_id: roleId,
        },
      },
    })

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error("Error revoking dashboard permission:", error)
    return NextResponse.json(
      { error: "Failed to revoke permission" },
      { status: 500 }
    )
  }
}
