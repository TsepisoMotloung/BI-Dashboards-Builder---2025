"use client"

import { useEffect, useRef, useState } from "react"
import dynamic from "next/dynamic"

// Dynamically import plotly.js to avoid SSR issues
const PlotlyComponent = dynamic(() => import("react-plotly.js"), {
  ssr: false,
  loading: () => <div className="text-gray-500">Loading chart...</div>,
})

interface VisualizationRendererProps {
  visualization: any
  config: any
  permissionFilters?: any
}

export default function VisualizationRenderer({
  visualization,
  config,
  permissionFilters,
}: VisualizationRendererProps) {
  const [plotData, setPlotData] = useState<any>([])
  const [layout, setLayout] = useState<any>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadVisualizationData = async () => {
      try {
        setLoading(true)
        setError(null)

        // For now, render placeholder based on visualization type
        // In a real app, this would fetch data from an API based on:
        // - visualization.query (custom SQL)
        // - config.dataModel (which table)
        // - config.measure (which column)
        // - permissionFilters (row-level security filters)

        const type = visualization.type || "line"

        // Mock data for demonstration
        const mockData = {
          line: [
            {
              x: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
              y: [10, 15, 13, 17, 20, 18],
              mode: "lines+markers",
              type: "scatter",
              name: config.measure || "Value",
            },
          ],
          bar: [
            {
              x: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
              y: [10, 15, 13, 17, 20, 18],
              type: "bar",
              name: config.measure || "Value",
            },
          ],
          pie: [
            {
              labels: ["Category A", "Category B", "Category C"],
              values: [30, 40, 30],
              type: "pie",
            },
          ],
          scatter: [
            {
              x: [1, 2, 3, 4, 5, 6],
              y: [10, 15, 13, 17, 20, 18],
              mode: "markers",
              type: "scatter",
              name: config.measure || "Value",
            },
          ],
          table: [
            {
              type: "table",
              header: {
                values: ["Column A", "Column B", "Column C"],
              },
              cells: {
                values: [
                  ["Value 1", "Value 2", "Value 3"],
                  ["Value 4", "Value 5", "Value 6"],
                  ["Value 7", "Value 8", "Value 9"],
                ],
              },
            },
          ],
        }

        const data = (mockData as any)[type] || mockData.line

        setPlotData(data)
        setLayout({
          title: config.title || "",
          autosize: true,
          margin: { l: 50, r: 20, t: 40, b: 40 },
          hovermode: "closest",
          xaxis: { title: config.xAxis || "" },
          yaxis: { title: config.yAxis || "" },
        })
      } catch (err: any) {
        setError(err.message || "Failed to load visualization")
      } finally {
        setLoading(false)
      }
    }

    loadVisualizationData()
  }, [visualization, config, permissionFilters])

  if (error) {
    return <div className="text-red-600 text-sm">{error}</div>
  }

  if (loading) {
    return <div className="text-gray-500">Loading chart...</div>
  }

  return (
    <div className="w-full h-full">
      <PlotlyComponent
        data={plotData}
        layout={layout}
        config={{ responsive: true }}
        useResizeHandler
      />
    </div>
  )
}
