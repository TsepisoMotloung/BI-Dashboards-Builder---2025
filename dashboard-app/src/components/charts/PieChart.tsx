"use client"

import { ChartWrapper } from "./ChartWrapper"

interface PieChartProps {
  data: {
    labels: string[]
    values: number[]
    colors?: string[]
  }
  title?: string
  height?: number
  showLegend?: boolean
}

export function PieChart({
  data,
  title,
  height = 400,
  showLegend = true,
}: PieChartProps) {
  const trace = {
    labels: data.labels,
    values: data.values,
    type: "pie" as const,
    marker: {
      colors: data.colors || [
        "#3B82F6",
        "#10B981",
        "#F59E0B",
        "#EF4444",
        "#8B5CF6",
        "#EC4899",
        "#06B6D4",
      ],
    },
    textinfo: "label+percent",
    textposition: "inside",
    automargin: true,
  }

  const layout = {
    title: title || "",
    height,
    showlegend: showLegend,
    legend: {
      orientation: "v" as const,
      x: 1,
      y: 0.5,
    },
  }

  return <ChartWrapper data={[trace]} layout={layout} />
}
