"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import {
  LayoutDashboard,
  Users,
  Database,
  Upload,
  Settings,
  BarChart3,
  Shield,
  FileText,
} from "lucide-react"

interface SidebarProps {
  userRoles?: string[]
}

export function Sidebar({ userRoles = [] }: SidebarProps) {
  const pathname = usePathname()
  const isAdmin = userRoles.includes("Super Admin") || userRoles.includes("Admin")

  const navigation = [
    {
      name: "Dashboard",
      href: "/dashboard",
      icon: LayoutDashboard,
      roles: ["all"],
    },
    {
      name: "My Dashboards",
      href: "/dashboard/my-dashboards",
      icon: BarChart3,
      roles: ["all"],
    },
    {
      name: "Data Models",
      href: "/dashboard/data-models",
      icon: Database,
      roles: ["all"],
    },
    {
      name: "Upload Data",
      href: "/dashboard/uploads",
      icon: Upload,
      roles: ["all"],
    },
    {
      name: "Users",
      href: "/dashboard/admin/users",
      icon: Users,
      roles: ["Super Admin", "Admin"],
    },
    {
      name: "Roles & Permissions",
      href: "/dashboard/admin/roles",
      icon: Shield,
      roles: ["Super Admin"],
    },
    {
      name: "Audit Logs",
      href: "/dashboard/admin/audit",
      icon: FileText,
      roles: ["Super Admin", "Admin"],
    },
    {
      name: "Settings",
      href: "/dashboard/settings",
      icon: Settings,
      roles: ["all"],
    },
  ]

  const filteredNavigation = navigation.filter((item) => {
    if (item.roles.includes("all")) return true
    return item.roles.some((role) => userRoles.includes(role))
  })

  return (
    <div className="flex h-full w-64 flex-col border-r bg-card">
      <div className="flex h-16 items-center border-b px-6">
        <Link href="/dashboard" className="flex items-center space-x-2">
          <BarChart3 className="h-6 w-6 text-primary" />
          <span className="text-xl font-bold">BI Dashboard</span>
        </Link>
      </div>

      <nav className="flex-1 space-y-1 p-4">
        {filteredNavigation.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/")
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center space-x-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <item.icon className="h-5 w-5" />
              <span>{item.name}</span>
            </Link>
          )
        })}
      </nav>

      <div className="border-t p-4">
        <div className="text-xs text-muted-foreground">
          <p>Version 1.0.0</p>
          <p className="mt-1">© 2025 BI Dashboard</p>
        </div>
      </div>
    </div>
  )
}
