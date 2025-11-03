"use client"

import { ChartWrapper } from "./ChartWrapper"

interface ScatterChartProps {
  data: {
    x: number[]
    y: number[]
    name?: string
    color?: string
    size?: number[]
  }[]
  title?: string
  xAxisTitle?: string
  yAxisTitle?: string
  height?: number
}

export function ScatterChart({
  data,
  title,
  xAxisTitle,
  yAxisTitle,
  height = 400,
}: ScatterChartProps) {
  const traces = data.map((series) => ({
    x: series.x,
    y: series.y,
    type: "scatter" as const,
    mode: "markers" as const,
    name: series.name || "",
    marker: {
      color: series.color || "#3B82F6",
      size: series.size || 8,
      opacity: 0.7,
    },
  }))

  const layout = {
    title: title || "",
    xaxis: {
      title: xAxisTitle || "",
      showgrid: true,
      gridcolor: "#E5E7EB",
      zeroline: false,
    },
    yaxis: {
      title: yAxisTitle || "",
      showgrid: true,
      gridcolor: "#E5E7EB",
      zeroline: false,
    },
    height,
    showlegend: data.length > 1,
  }

  return <ChartWrapper data={traces} layout={layout} />
}
