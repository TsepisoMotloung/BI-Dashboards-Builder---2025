import { redirect } from "next/navigation"

// Redirect to viewer page for dashboard viewing
export default function DashboardViewPage({ params }: { params: { id: string } }) {
  redirect(`/dashboard/viewer/${params.id}`)
}
