import React from "react"
import { Card } from "@/components/ui/Card"

export function DashboardTabs({ tabs }: { tabs: any[] }) {
  const active = tabs[0]

  return (
    <div>
      <div className="mb-4">
        <div className="flex gap-4 border-b">
          {tabs.map((t) => (
            <button key={t.id} className={`px-4 py-2 ${t.id === active.id ? "text-blue-600 border-b-2 border-blue-500" : "text-gray-600"}`}>
              {t.name}
            </button>
          ))}
        </div>
      </div>

      <div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {active.visualizations.map((vis: any) => {
            const config = typeof vis.config === "string" ? JSON.parse(vis.config || "{}") : vis.config || {}
            return (
              <Card key={vis.id} className="p-4">
                <div className="text-sm font-semibold mb-2">{config.title || vis.type}</div>
                <div className="h-48 bg-gray-100 rounded flex items-center justify-center text-gray-500">{vis.type} visualization</div>
              </Card>
            )
          })}
        </div>
      </div>
    </div>
  )
}
