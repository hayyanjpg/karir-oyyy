import api from './api'
import type { ApplicationFilters } from '../types'

export function parseFilename(disposition?: string): string | null {
  if (!disposition) {
    return null
  }

  const utf8 = disposition.match(/filename\*=UTF-8''([^;]+)/i)
  if (utf8?.[1]) {
    try {
      return decodeURIComponent(utf8[1])
    } catch {
      return utf8[1]
    }
  }

  const plain = disposition.match(/filename="?([^";]+)"?/i)
  return plain?.[1] ?? null
}

export async function downloadReport(
  format: 'xlsx' | 'pdf',
  filters: ApplicationFilters,
): Promise<void> {
  const params = Object.fromEntries(
    Object.entries({ ...filters, format }).filter(
      ([, value]) => value !== undefined && value !== null && value !== '',
    ),
  )

  const response = await api.get<Blob>('/reports/export', {
    params,
    responseType: 'blob',
  })

  const filename =
    parseFilename(response.headers['content-disposition'] as string | undefined) ??
    `Laporan_Lamaran.${format}`

  const blob = response.data
  const objectUrl = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = objectUrl
  link.download = filename
  link.rel = 'noopener'
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(objectUrl)
}
