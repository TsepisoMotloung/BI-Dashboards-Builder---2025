"use client"

import { useEffect, useRef } from "react"
import Plotly from "plotly.js-dist-min"

interface ChartWrapperProps {
  data: any[]
  layout?: Partial<Plotly.Layout>
  config?: Partial<Plotly.Config>
  className?: string
}

export function ChartWrapper({ data, layout = {}, config = {}, className = "" }: ChartWrapperProps) {
  const chartRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!chartRef.current) return

    const defaultLayout: Partial<Plotly.Layout> = {
      autosize: true,
      margin: { l: 50, r: 50, t: 50, b: 50 },
      paper_bgcolor: "white",
      plot_bgcolor: "white",
      font: {
        family: "Inter, system-ui, sans-serif",
        size: 12,
      },
      ...layout,
    }

    const defaultConfig: Partial<Plotly.Config> = {
      responsive: true,
      displayModeBar: true,
      displaylogo: false,
      modeBarButtonsToRemove: ["pan2d", "lasso2d", "select2d"],
      ...config,
    }

    Plotly.newPlot(chartRef.current, data, defaultLayout, defaultConfig)

    // Cleanup
    return () => {
      if (chartRef.current) {
        Plotly.purge(chartRef.current)
      }
    }
  }, [data, layout, config])

  return <div ref={chartRef} className={className} style={{ width: "100%", height: "100%" }} />
}
