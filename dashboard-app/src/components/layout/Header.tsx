"use client"

import { useState } from "react"
import { signOut } from "next-auth/react"
import { Avatar } from "@/components/ui/Avatar"
import { Button } from "@/components/ui/Button"
import { getInitials } from "@/lib/utils"
import { LogOut, User, Settings, ChevronDown } from "lucide-react"

interface HeaderProps {
  user: {
    name?: string | null
    email?: string | null
    roles?: string[]
  }
}

export function Header({ user }: HeaderProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const handleSignOut = async () => {
    await signOut({ callbackUrl: "/auth/signin" })
  }

  return (
    <header className="flex h-16 items-center justify-between border-b bg-card px-6">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
      </div>

      <div className="flex items-center space-x-4">
        {/* User Role Badge */}
        {user.roles && user.roles.length > 0 && (
          <div className="hidden md:block">
            <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
              {user.roles[0]}
            </span>
          </div>
        )}

        {/* User Menu */}
        <div className="relative">
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="flex items-center space-x-3 rounded-lg px-3 py-2 hover:bg-accent transition-colors"
          >
            <Avatar fallback={getInitials(user.name || user.email || "U")} />
            <div className="hidden md:block text-left">
              <p className="text-sm font-medium">{user.name}</p>
              <p className="text-xs text-muted-foreground">{user.email}</p>
            </div>
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          </button>

          {/* Dropdown Menu */}
          {isMenuOpen && (
            <>
              <div
                className="fixed inset-0 z-10"
                onClick={() => setIsMenuOpen(false)}
              />
              <div className="absolute right-0 z-20 mt-2 w-56 rounded-lg border bg-card shadow-lg animate-fade-in">
                <div className="p-4 border-b">
                  <p className="text-sm font-medium">{user.name}</p>
                  <p className="text-xs text-muted-foreground">{user.email}</p>
                  {user.roles && user.roles.length > 0 && (
                    <p className="mt-2 text-xs">
                      <span className="rounded-full bg-primary/10 px-2 py-0.5 text-primary">
                        {user.roles[0]}
                      </span>
                    </p>
                  )}
                </div>
                <div className="p-2">
                  <button
                    onClick={() => {
                      setIsMenuOpen(false)
                      window.location.href = "/dashboard/settings/profile"
                    }}
                    className="flex w-full items-center space-x-2 rounded-md px-3 py-2 text-sm hover:bg-accent transition-colors"
                  >
                    <User className="h-4 w-4" />
                    <span>Profile</span>
                  </button>
                  <button
                    onClick={() => {
                      setIsMenuOpen(false)
                      window.location.href = "/dashboard/settings"
                    }}
                    className="flex w-full items-center space-x-2 rounded-md px-3 py-2 text-sm hover:bg-accent transition-colors"
                  >
                    <Settings className="h-4 w-4" />
                    <span>Settings</span>
                  </button>
                </div>
                <div className="border-t p-2">
                  <button
                    onClick={handleSignOut}
                    className="flex w-full items-center space-x-2 rounded-md px-3 py-2 text-sm text-destructive hover:bg-destructive/10 transition-colors"
                  >
                    <LogOut className="h-4 w-4" />
                    <span>Sign Out</span>
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
