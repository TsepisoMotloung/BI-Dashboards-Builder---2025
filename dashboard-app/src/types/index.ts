import { UserStatus } from "@prisma/client"

export interface User {
  id: number
  email: string
  full_name: string
  status: UserStatus
  created_at: Date
  updated_at: Date
}

export interface UserWithRoles extends User {
  roles: string[]
}

export interface Dashboard {
  id: number
  name: string
  description?: string
  layout?: Record<string, any>
  created_by?: number
  created_at: Date
  updated_at: Date
}

export interface DashboardTab {
  id: number
  dashboard_id: number
  name: string
  order: number
  config?: Record<string, any>
}

export interface Visualization {
  id: number
  tab_id: number
  type: string
  config: Record<string, any>
  query?: string
  order: number
  created_at: Date
  updated_at: Date
}

export interface DataModel {
  id: number
  name: string
  schema_json: Record<string, any>
  version: number
  created_at: Date
  updated_at: Date
}

export interface UploadHistory {
  id: number
  user_id?: number
  model_id: number
  file_name: string
  status: string
  records_count: number
  error_message?: string
  created_at: Date
  completed_at?: Date
}

export interface ChartData {
  x: any[]
  y: any[]
  type: string
  name?: string
  marker?: {
    color?: string
  }
}

export interface ChartLayout {
  title?: string
  xaxis?: {
    title?: string
  }
  yaxis?: {
    title?: string
  }
  height?: number
  width?: number
  showlegend?: boolean
}
