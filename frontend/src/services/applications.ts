import api from './api'
import type {
  AnalyticsSummary,
  Application,
  ApplicationFilters,
  ApplicationInput,
  ApplicationPage,
  SortField,
  SortOrder,
} from '../types'

function cleanParams(params: Record<string, unknown>): Record<string, unknown> {
  return Object.fromEntries(
    Object.entries(params).filter(
      ([, value]) => value !== undefined && value !== null && value !== '',
    ),
  )
}

export async function fetchApplications(
  filters: ApplicationFilters,
  page: number,
  pageSize: number,
  sort: SortField,
  order: SortOrder,
): Promise<ApplicationPage> {
  const { data } = await api.get<ApplicationPage>('/applications', {
    params: cleanParams({
      ...filters,
      page,
      page_size: pageSize,
      sort,
      order,
    }),
  })
  return data
}

export async function createApplication(payload: ApplicationInput): Promise<Application> {
  const { data } = await api.post<Application>('/applications', payload)
  return data
}

export async function updateApplication(
  id: string,
  payload: Partial<ApplicationInput>,
): Promise<Application> {
  const { data } = await api.patch<Application>(`/applications/${id}`, payload)
  return data
}

export async function deleteApplication(id: string): Promise<void> {
  await api.delete(`/applications/${id}`)
}

export async function fetchAnalytics(): Promise<AnalyticsSummary> {
  const { data } = await api.get<AnalyticsSummary>('/analytics/summary')
  return data
}
