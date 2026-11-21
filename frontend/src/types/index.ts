export const STATUS_OPTIONS = [
  'Applied',
  'Screening',
  'Technical Test',
  'HR Interview',
  'User Interview',
  'Offering',
  'Rejected',
  'Ghosted',
] as const

export type ApplicationStatus = (typeof STATUS_OPTIONS)[number]

export const WORK_MODEL_OPTIONS = ['WFO', 'Hybrid', 'Remote'] as const

export type WorkModel = (typeof WORK_MODEL_OPTIONS)[number]

export const PORTAL_OPTIONS = [
  'LinkedIn',
  'Glints',
  'JobStreet',
  'Kalibrr',
  'Website Perusahaan',
  'Lainnya',
] as const

export type JobPortal = (typeof PORTAL_OPTIONS)[number]

export type SortField = 'applied_date' | 'created_at' | 'updated_at' | 'company_name'
export type SortOrder = 'asc' | 'desc'

export interface User {
  id: string
  email: string
  full_name: string
  avatar_url: string | null
}

export interface Application {
  id: string
  company_name: string
  position_title: string
  status: ApplicationStatus
  applied_date: string
  job_portal: JobPortal
  work_model: WorkModel
  salary_range: string | null
  job_url: string | null
  notes: string | null
  created_at: string
  updated_at: string
  days_since_update: number
  needs_follow_up: boolean
}

export interface ApplicationPage {
  items: Application[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface ApplicationInput {
  company_name: string
  position_title: string
  status: ApplicationStatus
  applied_date: string
  job_portal: JobPortal
  work_model: WorkModel
  salary_range?: string | null
  job_url?: string | null
  notes?: string | null
}

export interface ApplicationFilters {
  search?: string
  status?: ApplicationStatus
  work_model?: WorkModel
  job_portal?: JobPortal
  start_date?: string
  end_date?: string
}

export interface KpiSummary {
  total: number
  active_pipeline: number
  interview_count: number
  interview_rate: number
  offerings: number
  rejected: number
  ghosted: number
}

export interface StatusCount {
  status: ApplicationStatus
  count: number
}

export interface PortalCount {
  portal: JobPortal
  count: number
}

export interface FollowUpItem {
  id: string
  company_name: string
  position_title: string
  status: ApplicationStatus
  updated_at: string
  days_since_update: number
}

export interface AnalyticsSummary {
  kpi: KpiSummary
  by_status: StatusCount[]
  by_portal: PortalCount[]
  follow_up: FollowUpItem[]
}
