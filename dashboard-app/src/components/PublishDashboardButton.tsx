"use client"

import { useState } from "react"
import { Button } from "@/components/ui/Button"

interface PublishDashboardButtonProps {
  dashboardId: number
  initialPublished: boolean
}

export default function PublishDashboardButton({
  dashboardId,
  initialPublished,
}: PublishDashboardButtonProps) {
  const [isPublished, setIsPublished] = useState(initialPublished)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleTogglePublish = async () => {
    setLoading(true)
    setError(null)

    try {
      const method = isPublished ? "DELETE" : "POST"
      const response = await fetch(
        `/api/dashboards/${dashboardId}/publish`,
        { method }
      )

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.error || "Failed to update publish status")
      }

      setIsPublished(!isPublished)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex items-center gap-2">
      {error && <span className="text-red-600 text-sm">{error}</span>}
      <Button
        onClick={handleTogglePublish}
        disabled={loading}
        variant={isPublished ? "secondary" : "default"}
      >
        {loading ? "Loading..." : isPublished ? "Unpublish" : "Publish"}
      </Button>
      {isPublished && (
        <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded">
          Published
        </span>
      )}
    </div>
  )
}
