"use client"

import { useState, useCallback, useEffect } from "react"
import { Button } from "@/components/ui/Button"
import { Card } from "@/components/ui/Card"

interface VisualizationConfig {
  id: number
  type: string
  config: Record<string, any>
  query?: string
  order: number
  x?: number
  y?: number
  width?: number
  height?: number
}

interface DashboardCanvasProps {
  tabId: number
  dashboardId: number
  isCreator: boolean
  initialVisualizations?: VisualizationConfig[]
  onVisualizationAdded?: (vis: VisualizationConfig) => void
}

const VISUALIZATION_TYPES = [
  { id: "line", label: "Line Chart", icon: "📈" },
  { id: "bar", label: "Bar Chart", icon: "📊" },
  { id: "pie", label: "Pie Chart", icon: "🥧" },
  { id: "scatter", label: "Scatter Chart", icon: "📍" },
  { id: "table", label: "Data Table", icon: "📋" },
  { id: "metric", label: "Metric Card", icon: "📌" },
]

export function DashboardCanvas({
  tabId,
  dashboardId,
  isCreator,
  initialVisualizations,
  onVisualizationAdded,
}: DashboardCanvasProps) {
  const [visualizations, setVisualizations] = useState<VisualizationConfig[]>(
    initialVisualizations || []
  )
  const [selectedVis, setSelectedVis] = useState<number | null>(null)
  const [showAddMenu, setShowAddMenu] = useState(false)
  const [isDragging, setIsDragging] = useState(false)
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 })
  const [editingVis, setEditingVis] = useState<VisualizationConfig | null>(null)
  const [editorState, setEditorState] = useState<{
    title: string
    query: string
    width: number
    height: number
    dataModel?: string
    measure?: string
  } | null>(null)
  const [dataModels, setDataModels] = useState<any[]>([])
  const [loadingModels, setLoadingModels] = useState(false)

  const handleAddVisualization = useCallback(
    async (type: string) => {
      if (!isCreator) return

      try {
        const response = await fetch(
          `/api/tabs/${tabId}/visualizations`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              type,
              config: {
                title: `New ${type} Chart`,
                width: 400,
                height: 300,
              },
            }),
          }
        )

        if (!response.ok) throw new Error("Failed to create visualization")

        const vis = await response.json()
        const parsedConfig = typeof vis.config === "string" ? JSON.parse(vis.config || "{}") : vis.config || {}
        const newVis: VisualizationConfig = {
          ...vis,
          config: parsedConfig,
          x: visualizations.length % 2 === 0 ? 20 : 440,
          y: Math.floor(visualizations.length / 2) * 340 + 20,
          width: 400,
          height: 300,
        }

        setVisualizations([...visualizations, newVis])
        onVisualizationAdded?.(newVis)
        setShowAddMenu(false)
      } catch (error) {
        console.error("Error adding visualization:", error)
        alert("Failed to add visualization")
      }
    },
    [tabId, isCreator, visualizations, onVisualizationAdded]
  )

  const handleDeleteVisualization = useCallback(
    async (id: number) => {
      try {
        const response = await fetch(
          `/api/tabs/${tabId}/visualizations?vis_id=${id}`,
          { method: "DELETE" }
        )

        if (!response.ok) throw new Error("Failed to delete visualization")

        setVisualizations(
          visualizations.filter((v) => v.id !== id)
        )
        setSelectedVis(null)
      } catch (error) {
        console.error("Error deleting visualization:", error)
        alert("Failed to delete visualization")
      }
    },
    [tabId, visualizations]
  )

  const handleMouseDown = (id: number, e: React.MouseEvent) => {
    if (!isCreator) return
    setSelectedVis(id)
    setIsDragging(true)

    const vis = visualizations.find((v) => v.id === id)
    if (vis) {
      const canvas = document.querySelector(".canvas-container") as HTMLElement
      const rect = canvas?.getBoundingClientRect()
      setDragOffset({
        x: e.clientX - (rect?.left || 0) - (vis.x || 0),
        y: e.clientY - (rect?.top || 0) - (vis.y || 0),
      })
    }
  }

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging || !selectedVis) return

    const canvas = document.querySelector(".canvas-container") as HTMLElement
    const rect = canvas?.getBoundingClientRect()
    if (!rect) return

    const newX = Math.max(0, e.clientX - rect.left - dragOffset.x)
    const newY = Math.max(0, e.clientY - rect.top - dragOffset.y)

    setVisualizations(
      visualizations.map((v) =>
        v.id === selectedVis ? { ...v, x: newX, y: newY } : v
      )
    )
  }

  const handleMouseUp = () => {
    setIsDragging(false)
  }

  useEffect(() => {
    // keep initialVisualizations if they change
    if (initialVisualizations) setVisualizations(initialVisualizations)
  }, [initialVisualizations])

  useEffect(() => {
    // Load data models on mount
    async function loadModels() {
      setLoadingModels(true)
      try {
        const res = await fetch("/api/data-models")
        if (res.ok) {
          const models = await res.json()
          setDataModels(models)
        }
      } catch (e) {
        console.error("Failed to load data models:", e)
      } finally {
        setLoadingModels(false)
      }
    }
    loadModels()
  }, [])

  const saveLayout = useCallback(async () => {
    try {
      const payload = {
        layout: {
          tabs: [
            {
              id: tabId,
              visualizations: visualizations.map((v) => ({
                id: v.id,
                x: v.x ?? 0,
                y: v.y ?? 0,
                width: v.width ?? 400,
                height: v.height ?? 300,
                order: v.order,
              })),
            },
          ],
        },
      }

      const res = await fetch(`/api/dashboards/${dashboardId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })

      if (!res.ok) throw new Error("Failed to save layout")
      alert("Layout saved")
    } catch (e) {
      console.error("saveLayout error", e)
      alert("Failed to save layout")
    }
  }, [dashboardId, tabId, visualizations])

  return (
    <div className="flex flex-col h-full gap-4">
      {/* Toolbar */}
      {isCreator && (
        <div className="flex gap-2">
          <div className="relative">
            <Button
              onClick={() => setShowAddMenu(!showAddMenu)}
              variant="default"
            >
              + Add Visualization
            </Button>

            {showAddMenu && (
              <div className="absolute top-12 left-0 bg-white border border-gray-300 rounded-lg shadow-lg z-10 p-2 min-w-48">
                {VISUALIZATION_TYPES.map((type) => (
                  <button
                    key={type.id}
                    onClick={() => handleAddVisualization(type.id)}
                    className="w-full text-left px-4 py-2 hover:bg-gray-100 rounded flex items-center gap-2"
                  >
                    <span className="text-lg">{type.icon}</span>
                    <span className="text-sm">{type.label}</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {selectedVis && (
            <Button
              onClick={() => handleDeleteVisualization(selectedVis)}
              variant="secondary"
              className="bg-red-500 hover:bg-red-600 text-white"
            >
              Delete Selected
            </Button>
          )}
          <Button onClick={saveLayout} variant="outline">
            Save Layout
          </Button>
        </div>
      )}

      {/* Canvas */}
      <div
        className="canvas-container flex-1 bg-gray-50 border border-gray-300 rounded-lg overflow-auto relative"
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        {visualizations.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-400 pointer-events-none">
            {isCreator
              ? "Drag and drop visualizations here or use the toolbar to add"
              : "No visualizations added yet"}
          </div>
        ) : (
          <div className="relative" style={{ minHeight: "2000px" }}>
            {visualizations.map((vis) => (
              <div
                key={vis.id}
                className={`absolute bg-white border-2 rounded-lg shadow-sm cursor-move p-3 transition-colors ${
                  selectedVis === vis.id
                    ? "border-blue-500 bg-blue-50"
                    : "border-gray-200 hover:border-gray-300"
                }`}
                style={{
                  left: `${vis.x || 0}px`,
                  top: `${vis.y || 0}px`,
                  width: `${vis.width || 400}px`,
                  height: `${vis.height || 300}px`,
                }}
                onMouseDown={(e) => handleMouseDown(vis.id, e)}
                onClick={() => setSelectedVis(vis.id)}
                onDoubleClick={() => {
                  if (!isCreator) return
                  const cfg = typeof vis.config === "string" ? JSON.parse(vis.config || "{}") : vis.config || {}
                  setEditingVis({ ...vis, config: cfg })
                  setEditorState({
                    title: (cfg && (cfg.title || cfg.name)) || "",
                    query: (vis.query as string) || "",
                    width: vis.width || cfg.width || 400,
                    height: vis.height || cfg.height || 300,
                    dataModel: cfg.dataModel || "",
                    measure: cfg.measure || "",
                  })
                }}
              >
                <div className="text-xs font-semibold text-gray-600 mb-2">
                  {VISUALIZATION_TYPES.find((t) => t.id === vis.type)
                    ?.label || vis.type}
                </div>
                <div className="flex-1 flex items-center justify-center text-gray-400 text-sm min-h-32">
                  <span>
                    {isCreator ? "Double-click to configure" : "Visualization"}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Properties Panel */}
      {selectedVis && isCreator && (
        <Card className="p-4 bg-gray-50 border-t">
          <div className="text-sm text-gray-600">
            <p>
              <strong>ID:</strong> {selectedVis}
            </p>
            <p className="text-xs mt-1 text-gray-500">
              Drag to move, use toolbar to delete
            </p>
          </div>
        </Card>
      )}

      {/* Visualization Editor Modal */}
      {editingVis && editorState && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black opacity-30" onClick={() => { setEditingVis(null); setEditorState(null) }} />
          <div className="bg-white rounded-lg shadow-lg z-60 w-11/12 max-w-xl p-6">
            <h3 className="text-lg font-semibold mb-4">Edit Visualization</h3>

            <div className="space-y-3">
              <div>
                <label className="block text-sm text-gray-700 mb-1">Title</label>
                <input
                  className="w-full border px-3 py-2 rounded"
                  value={editorState.title}
                  onChange={(e) => setEditorState({ ...editorState, title: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm text-gray-700 mb-1">Data Model</label>
                <select
                  className="w-full border px-3 py-2 rounded"
                  value={editorState.dataModel || ""}
                  onChange={(e) => setEditorState({ ...editorState, dataModel: e.target.value })}
                  disabled={loadingModels}
                >
                  <option value="">Select a data model...</option>
                  {dataModels.map((m) => (
                    <option key={m.id} value={m.name}>
                      {m.name}
                    </option>
                  ))}
                </select>
              </div>

              {editorState.dataModel && (
                <div>
                  <label className="block text-sm text-gray-700 mb-1">Column / Measure</label>
                  <select
                    className="w-full border px-3 py-2 rounded"
                    value={editorState.measure || ""}
                    onChange={(e) => setEditorState({ ...editorState, measure: e.target.value })}
                  >
                    <option value="">Select a column...</option>
                    {dataModels
                      .find((m) => m.name === editorState.dataModel)
                      ?.columns?.map((col: string) => (
                        <option key={col} value={col}>
                          {col}
                        </option>
                      ))}
                  </select>
                </div>
              )}

              <div>
                <label className="block text-sm text-gray-700 mb-1">Query / Custom SQL</label>
                <textarea
                  className="w-full border px-3 py-2 rounded h-20"
                  value={editorState.query}
                  onChange={(e) => setEditorState({ ...editorState, query: e.target.value })}
                  placeholder="Optional: SQL or query string to override data model"
                />
              </div>

              <div className="flex gap-2">
                <div className="flex-1">
                  <label className="block text-sm text-gray-700 mb-1">Width</label>
                  <input
                    type="number"
                    className="w-full border px-3 py-2 rounded"
                    value={editorState.width}
                    onChange={(e) => setEditorState({ ...editorState, width: Number(e.target.value) })}
                  />
                </div>
                <div className="flex-1">
                  <label className="block text-sm text-gray-700 mb-1">Height</label>
                  <input
                    type="number"
                    className="w-full border px-3 py-2 rounded"
                    value={editorState.height}
                    onChange={(e) => setEditorState({ ...editorState, height: Number(e.target.value) })}
                  />
                </div>
              </div>
            </div>

            <div className="mt-4 flex justify-end gap-2">
              <button
                className="px-4 py-2 bg-gray-100 rounded"
                onClick={() => { setEditingVis(null); setEditorState(null) }}
              >
                Cancel
              </button>
              <button
                className="px-4 py-2 bg-blue-600 text-white rounded"
                onClick={async () => {
                  try {
                    const resp = await fetch(`/api/tabs/${tabId}/visualizations?vis_id=${editingVis.id}`, {
                      method: "PUT",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({
                        config: { 
                          ...editingVis.config, 
                          title: editorState.title, 
                          width: editorState.width, 
                          height: editorState.height,
                          dataModel: editorState.dataModel || undefined,
                          measure: editorState.measure || undefined,
                        },
                        query: editorState.query,
                      }),
                    })

                    if (!resp.ok) throw new Error("Failed to update visualization")
                    const updated = await resp.json()

                    setVisualizations((prev) => prev.map((v) => (v.id === updated.id ? { ...v, config: typeof updated.config === "string" ? JSON.parse(updated.config || "{}") : updated.config, query: updated.query, width: editorState.width, height: editorState.height } : v)))
                    setEditingVis(null)
                    setEditorState(null)
                  } catch (e) {
                    console.error("Failed to save visualization", e)
                    alert("Failed to save visualization")
                  }
                }}
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
