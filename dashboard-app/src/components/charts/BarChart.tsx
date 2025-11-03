"use client"

import { ChartWrapper } from "./ChartWrapper"

interface BarChartProps {
  data: {
    x: (string | number)[]
    y: number[]
    name?: string
    color?: string
  }[]
  title?: string
  xAxisTitle?: string
  yAxisTitle?: string
  horizontal?: boolean
  stacked?: boolean
  height?: number
}

export function BarChart({
  data,
  title,
  xAxisTitle,
  yAxisTitle,
  horizontal = false,
  stacked = false,
  height = 400,
}: BarChartProps) {
  const traces = data.map((series) => ({
    x: horizontal ? series.y : series.x,
    y: horizontal ? series.x : series.y,
    type: "bar" as const,
    name: series.name || "",
    marker: {
      color: series.color || "#3B82F6",
    },
    orientation: horizontal ? ("h" as const) : ("v" as const),
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
    barmode: stacked ? ("stack" as const) : ("group" as const),
    height,
    showlegend: data.length > 1,
  }

  return <ChartWrapper data={traces} layout={layout} />
}
