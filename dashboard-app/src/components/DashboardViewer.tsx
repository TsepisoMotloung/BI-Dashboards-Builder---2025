"use client"

import { useState, useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import VisualizationRenderer from "@/components/VisualizationRenderer"

interface DashboardViewerProps {
  dashboard: any
  userPermission: any
  isCreator: boolean
}

export default function DashboardViewer({
  dashboard,
  userPermission,
  isCreator,
}: DashboardViewerProps) {
  const [activeTabId, setActiveTabId] = useState(
    dashboard.tabs[0]?.id || null
  )

  const activeTab = useMemo(
    () => dashboard.tabs.find((t: any) => t.id === activeTabId),
    [activeTabId, dashboard.tabs]
  )

  if (!activeTab) {
    return (
      <div className="p-8 text-center text-gray-500">
        No tabs available in this dashboard
      </div>
    )
  }

  // Extract filters from permission if available
  const permissionFilters = useMemo(() => {
    if (!userPermission) return null
    try {
      const perms = typeof userPermission.permissions === "string"
        ? JSON.parse(userPermission.permissions)
        : userPermission.permissions
      return perms?.filters || null
    } catch (e) {
      return null
    }
  }, [userPermission])

  return (
    <>
      {/* Tabs Bar */}
      {dashboard.tabs.length > 1 && (
        <div className="border-b border-gray-200 px-4 flex gap-4 bg-gray-50">
          {dashboard.tabs.map((tab: any) => (
            <button
              key={tab.id}
              onClick={() => setActiveTabId(tab.id)}
              className={`px-4 py-3 font-medium border-b-2 transition-colors ${
                tab.id === activeTabId
                  ? "border-blue-500 text-blue-600 bg-white"
                  : "border-transparent text-gray-600 hover:text-gray-900"
              }`}
            >
              {tab.name}
            </button>
          ))}
        </div>
      )}

      {/* Visualizations Grid */}
      <div className="flex-1 overflow-auto p-4">
        {activeTab.visualizations.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            <p>No visualizations in this tab yet</p>
          </div>
        ) : (
          <div className="grid gap-6 auto-rows-max">
            {activeTab.visualizations.map((vis: any) => {
              let config: any = {}
              try {
                config = typeof vis.config === "string"
                  ? JSON.parse(vis.config || "{}")
                  : vis.config || {}
              } catch (e) {
                config = {}
              }

              return (
                <Card
                  key={vis.id}
                  style={{
                    width: `${config.width || 400}px`,
                    height: `${config.height || 300}px`,
                  }}
                  className="flex flex-col"
                >
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">
                      {config.title || vis.type}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="flex-1 overflow-auto">
                    <VisualizationRenderer
                      visualization={vis}
                      config={config}
                      permissionFilters={permissionFilters}
                    />
                  </CardContent>
                </Card>
              )
            })}
          </div>
        )}
      </div>
    </>
  )
}
