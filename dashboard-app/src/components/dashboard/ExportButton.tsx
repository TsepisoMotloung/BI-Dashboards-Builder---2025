"use client"

import { useState } from "react"
import { Button } from "@/components/ui/Button"
import { Download } from "lucide-react"
import { exportToPDF, exportDashboardToPDF } from "@/lib/pdf-export"

interface ExportButtonProps {
  elementId?: string
  elementIds?: string[]
  dashboardName?: string
  variant?: "default" | "outline"
  size?: "default" | "sm" | "lg"
}

export function ExportButton({
  elementId,
  elementIds,
  dashboardName = "Dashboard",
  variant = "outline",
  size = "sm",
}: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false)

  const handleExport = async () => {
    setIsExporting(true)
    
    try {
      if (elementIds && elementIds.length > 0) {
        // Export multiple pages
        await exportDashboardToPDF(dashboardName, elementIds)
      } else if (elementId) {
        // Export single element
        await exportToPDF(elementId, {
          title: dashboardName,
          filename: `${dashboardName.toLowerCase().replace(/\s+/g, "-")}.pdf`,
        })
      }
    } catch (error) {
      console.error("Export failed:", error)
      alert("Failed to export PDF. Please try again.")
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <Button
      variant={variant}
      size={size}
      onClick={handleExport}
      disabled={isExporting}
    >
      <Download className="h-4 w-4 mr-2" />
      {isExporting ? "Exporting..." : "Export PDF"}
    </Button>
  )
}
