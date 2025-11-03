"use client"

import { ChartWrapper } from "./ChartWrapper"

interface LineChartProps {
  data: {
    x: (string | number | Date)[]
    y: number[]
    name?: string
    color?: string
    mode?: "lines" | "markers" | "lines+markers"
  }[]
  title?: string
  xAxisTitle?: string
  yAxisTitle?: string
  height?: number
}

export function LineChart({
  data,
  title,
  xAxisTitle,
  yAxisTitle,
  height = 400,
}: LineChartProps) {
  const traces = data.map((series) => ({
    x: series.x,
    y: series.y,
    type: "scatter" as const,
    mode: series.mode || ("lines+markers" as const),
    name: series.name || "",
    line: {
      color: series.color || "#3B82F6",
      width: 2,
    },
    marker: {
      size: 6,
    },
  }))

  const layout = {
    title: title || "",
    xaxis: {
      title: xAxisTitle || "",
      showgrid: true,
      gridcolor: "#E5E7EB",
    },
    yaxis: {
      title: yAxisTitle || "",
      showgrid: true,
      gridcolor: "#E5E7EB",
    },
    height,
    showlegend: data.length > 1,
  }

  return <ChartWrapper data={traces} layout={layout} />
}
