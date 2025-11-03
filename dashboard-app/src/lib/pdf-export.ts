"use client"

import jsPDF from "jspdf"
import html2canvas from "html2canvas"

export interface ExportOptions {
  filename?: string
  title?: string
  orientation?: "portrait" | "landscape"
  quality?: number
}

/**
 * Export a DOM element to PDF
 */
export async function exportToPDF(
  elementId: string,
  options: ExportOptions = {}
): Promise<void> {
  const {
    filename = "dashboard-export.pdf",
    title = "Dashboard Export",
    orientation = "landscape",
    quality = 0.95,
  } = options

  try {
    const element = document.getElementById(elementId)
    if (!element) {
      throw new Error(`Element with id "${elementId}" not found`)
    }

    // Show loading indicator
    const loadingEl = document.createElement("div")
    loadingEl.id = "pdf-loading"
    loadingEl.innerHTML = `
      <div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; 
                  background: rgba(0,0,0,0.8); display: flex; align-items: center; 
                  justify-content: center; z-index: 9999;">
        <div style="background: white; padding: 2rem; border-radius: 0.5rem; text-align: center;">
          <div style="font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem;">
            Generating PDF...
          </div>
          <div style="color: #6B7280;">This may take a moment</div>
        </div>
      </div>
    `
    document.body.appendChild(loadingEl)

    // Capture element as canvas
    const canvas = await html2canvas(element, {
      scale: 2, // Higher quality
      useCORS: true,
      logging: false,
      backgroundColor: "#ffffff",
    })

    // Calculate dimensions
    const imgWidth = orientation === "portrait" ? 210 : 297 // A4 in mm
    const imgHeight = (canvas.height * imgWidth) / canvas.width

    // Create PDF
    const pdf = new jsPDF({
      orientation,
      unit: "mm",
      format: "a4",
    })

    // Add title
    pdf.setFontSize(16)
    pdf.text(title, 14, 15)

    // Add date
    pdf.setFontSize(10)
    pdf.setTextColor(100)
    pdf.text(
      `Generated on ${new Date().toLocaleDateString()} at ${new Date().toLocaleTimeString()}`,
      14,
      22
    )

    // Add image
    const imgData = canvas.toDataURL("image/jpeg", quality)
    pdf.addImage(imgData, "JPEG", 10, 30, imgWidth - 20, imgHeight - 30)

    // Save PDF
    pdf.save(filename)

    // Remove loading indicator
    document.body.removeChild(loadingEl)

    return Promise.resolve()
  } catch (error) {
    console.error("Error exporting to PDF:", error)
    
    // Remove loading indicator if it exists
    const loadingEl = document.getElementById("pdf-loading")
    if (loadingEl) {
      document.body.removeChild(loadingEl)
    }

    throw error
  }
}

/**
 * Export dashboard with multiple pages
 */
export async function exportDashboardToPDF(
  dashboardName: string,
  elementIds: string[]
): Promise<void> {
  try {
    const pdf = new jsPDF({
      orientation: "landscape",
      unit: "mm",
      format: "a4",
    })

    // Show loading
    const loadingEl = document.createElement("div")
    loadingEl.id = "pdf-loading"
    loadingEl.innerHTML = `
      <div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; 
                  background: rgba(0,0,0,0.8); display: flex; align-items: center; 
                  justify-content: center; z-index: 9999;">
        <div style="background: white; padding: 2rem; border-radius: 0.5rem; text-align: center;">
          <div style="font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem;">
            Generating PDF...
          </div>
          <div style="color: #6B7280;">Page 1 of ${elementIds.length}</div>
        </div>
      </div>
    `
    document.body.appendChild(loadingEl)

    for (let i = 0; i < elementIds.length; i++) {
      const element = document.getElementById(elementIds[i])
      if (!element) continue

      // Update loading
      const loadingText = loadingEl.querySelector("div:last-child")
      if (loadingText) {
        loadingText.textContent = `Page ${i + 1} of ${elementIds.length}`
      }

      const canvas = await html2canvas(element, {
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: "#ffffff",
      })

      const imgWidth = 277 // A4 landscape width in mm (minus margins)
      const imgHeight = (canvas.height * imgWidth) / canvas.width

      if (i > 0) {
        pdf.addPage()
      }

      // Add header
      pdf.setFontSize(14)
      pdf.text(dashboardName, 14, 15)
      pdf.setFontSize(8)
      pdf.setTextColor(100)
      pdf.text(`Page ${i + 1} of ${elementIds.length}`, 14, 20)

      // Add image
      const imgData = canvas.toDataURL("image/jpeg", 0.95)
      pdf.addImage(imgData, "JPEG", 10, 25, imgWidth, imgHeight)
    }

    // Remove loading
    document.body.removeChild(loadingEl)

    // Save
    const filename = `${dashboardName.toLowerCase().replace(/\s+/g, "-")}-${Date.now()}.pdf`
    pdf.save(filename)

    return Promise.resolve()
  } catch (error) {
    console.error("Error exporting dashboard to PDF:", error)
    
    const loadingEl = document.getElementById("pdf-loading")
    if (loadingEl) {
      document.body.removeChild(loadingEl)
    }

    throw error
  }
}

/**
 * Export single chart to PDF
 */
export async function exportChartToPDF(
  chartElementId: string,
  chartTitle: string
): Promise<void> {
  return exportToPDF(chartElementId, {
    filename: `${chartTitle.toLowerCase().replace(/\s+/g, "-")}-chart.pdf`,
    title: chartTitle,
    orientation: "landscape",
  })
}
