"use client"

import React, { useState } from "react"

interface RoleItem {
  id: number
  name: string
}

interface PermissionItem {
  dashboard_id: number
  role_id: number
  permissions_json: string
  role: RoleItem
}

export function DashboardPermissionsManager({
  dashboardId,
  roles,
  initialPermissions,
}: {
  dashboardId: number
  roles: RoleItem[]
  initialPermissions: PermissionItem[]
}) {
  const [permissions, setPermissions] = useState<PermissionItem[]>(initialPermissions || [])
  const [loadingRoleId, setLoadingRoleId] = useState<number | null>(null)
  const [editingRoleId, setEditingRoleId] = useState<number | null>(null)
  const [editJson, setEditJson] = useState<string>("")

  const hasPermission = (roleId: number) => permissions.some((p) => p.role_id === roleId)

  function getPermissionForRole(roleId: number) {
    return permissions.find((p) => p.role_id === roleId)
  }

  function openEditor(roleId: number) {
    const p = getPermissionForRole(roleId)
    setEditingRoleId(roleId)
    setEditJson(p ? p.permissions_json : JSON.stringify({ view: true }, null, 2))
  }

  async function savePermission(roleId: number) {
    setLoadingRoleId(roleId)
    try {
      // validate JSON
      let parsed
      try {
        parsed = JSON.parse(editJson)
      } catch (e) {
        alert("Invalid JSON for permissions")
        return
      }

      const res = await fetch(`/api/dashboards/${dashboardId}/permissions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role_id: roleId, permissions: parsed }),
      })
      if (!res.ok) throw new Error("Failed to save permission")
      const created = await res.json()

      setPermissions((p) => {
        const filtered = p.filter((x) => x.role_id !== roleId)
        return [...filtered, created]
      })

      setEditingRoleId(null)
    } catch (e) {
      console.error(e)
      alert("Failed to save permission")
    } finally {
      setLoadingRoleId(null)
    }
  }

  async function grant(roleId: number) {
    // open editor with default and save immediately
    openEditor(roleId)
  }

  async function revoke(roleId: number) {
    setLoadingRoleId(roleId)
    try {
      const res = await fetch(`/api/dashboards/${dashboardId}/permissions?role_id=${roleId}`, {
        method: "DELETE",
      })
      if (!res.ok) throw new Error("Failed to revoke")
      setPermissions((p) => p.filter((x) => x.role_id !== roleId))
    } catch (e) {
      console.error(e)
      alert("Failed to revoke permission")
    } finally {
      setLoadingRoleId(null)
    }
  }

  return (
    <div className="space-y-3">
      {roles.map((r) => {
        const p = getPermissionForRole(r.id)
        return (
          <div key={r.id} className="p-3 border rounded">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="font-medium">{r.name}</div>
                <div className="text-xs text-gray-500">Role id: {r.id}</div>
                {p && (
                  <pre className="mt-2 text-xs bg-gray-100 p-2 rounded max-h-40 overflow-auto">{p.permissions_json}</pre>
                )}
              </div>

              <div className="flex flex-col items-end gap-2">
                {p ? (
                  <>
                    <div className="flex gap-2">
                      <button
                        className="px-3 py-1 bg-yellow-500 text-white rounded"
                        onClick={() => openEditor(r.id)}
                        disabled={loadingRoleId === r.id}
                      >
                        Edit
                      </button>
                      <button
                        className="px-3 py-1 bg-red-600 text-white rounded"
                        onClick={() => revoke(r.id)}
                        disabled={loadingRoleId === r.id}
                      >
                        {loadingRoleId === r.id ? "Working..." : "Revoke"}
                      </button>
                    </div>
                  </>
                ) : (
                  <div>
                    <button
                      className="px-3 py-1 bg-green-600 text-white rounded"
                      onClick={() => openEditor(r.id)}
                      disabled={loadingRoleId === r.id}
                    >
                      {loadingRoleId === r.id ? "Working..." : "Grant"}
                    </button>
                  </div>
                )}
              </div>
            </div>

            {editingRoleId === r.id && (
              <div className="mt-3">
                <label className="block text-sm text-gray-700 mb-1">Permissions JSON</label>
                <textarea
                  className="w-full border p-2 rounded h-40 font-mono text-xs"
                  value={editJson}
                  onChange={(e) => setEditJson(e.target.value)}
                />
                <div className="flex justify-end gap-2 mt-2">
                  <button
                    className="px-3 py-1 bg-gray-100 rounded"
                    onClick={() => { setEditingRoleId(null); setEditJson("") }}
                  >
                    Cancel
                  </button>
                  <button
                    className="px-3 py-1 bg-blue-600 text-white rounded"
                    onClick={() => savePermission(r.id)}
                    disabled={loadingRoleId === r.id}
                  >
                    {loadingRoleId === r.id ? "Saving..." : "Save"}
                  </button>
                </div>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
