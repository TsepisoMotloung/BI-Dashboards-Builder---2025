"use client"

import { useState, useEffect } from "react"

interface Column {
  name: string
}

interface DataModelItem {
  id: number
  name: string
  version: number
  columns: string[]
  relationships: {
    outbound: any[]
    inbound: any[]
  }
}

export function DataModelViewer() {
  const [models, setModels] = useState<DataModelItem[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedModel, setSelectedModel] = useState<DataModelItem | null>(null)

  useEffect(() => {
    async function loadModels() {
      try {
        const res = await fetch("/api/data-models")
        if (!res.ok) throw new Error("Failed to load models")
        const data = await res.json()
        setModels(data)
        if (data.length > 0) setSelectedModel(data[0])
      } catch (e) {
        console.error("Error loading data models:", e)
      } finally {
        setLoading(false)
      }
    }
    loadModels()
  }, [])

  if (loading) return <div className="p-4 text-gray-500">Loading data models...</div>

  if (models.length === 0) {
    return <div className="p-4 text-gray-500">No data models available</div>
  }

  return (
    <div className="flex gap-4 h-full">
      {/* Model List */}
      <div className="w-1/3 border-r p-4 overflow-auto">
        <h3 className="font-semibold mb-3">Data Models</h3>
        <div className="space-y-2">
          {models.map((m) => (
            <button
              key={m.id}
              onClick={() => setSelectedModel(m)}
              className={`w-full text-left p-2 rounded transition-colors ${
                selectedModel?.id === m.id
                  ? "bg-blue-100 border border-blue-500"
                  : "hover:bg-gray-100"
              }`}
            >
              <div className="font-medium text-sm">{m.name}</div>
              <div className="text-xs text-gray-500">v{m.version}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Model Details */}
      {selectedModel && (
        <div className="flex-1 p-4 overflow-auto">
          <div>
            <h3 className="text-lg font-semibold mb-1">{selectedModel.name}</h3>
            <p className="text-xs text-gray-500 mb-4">Version {selectedModel.version}</p>

            {/* Columns */}
            {selectedModel.columns.length > 0 && (
              <div className="mb-4">
                <h4 className="font-medium text-sm mb-2">Columns</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedModel.columns.map((col, i) => (
                    <div
                      key={i}
                      className="px-2 py-1 bg-blue-50 border border-blue-200 rounded text-xs"
                    >
                      {col}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Relationships */}
            {(selectedModel.relationships.outbound.length > 0 ||
              selectedModel.relationships.inbound.length > 0) && (
              <div>
                <h4 className="font-medium text-sm mb-2">Relationships</h4>

                {selectedModel.relationships.outbound.length > 0 && (
                  <div className="mb-3">
                    <div className="text-xs font-semibold text-gray-600 mb-1">
                      Connects to:
                    </div>
                    <div className="space-y-1">
                      {selectedModel.relationships.outbound.map((r: any) => (
                        <div key={r.id} className="text-xs p-1 bg-gray-50 rounded">
                          {selectedModel.name} → {r.targetModel} ({r.type})
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {selectedModel.relationships.inbound.length > 0 && (
                  <div>
                    <div className="text-xs font-semibold text-gray-600 mb-1">
                      Connected from:
                    </div>
                    <div className="space-y-1">
                      {selectedModel.relationships.inbound.map((r: any) => (
                        <div key={r.id} className="text-xs p-1 bg-gray-50 rounded">
                          {r.sourceModel} → {selectedModel.name} ({r.type})
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
