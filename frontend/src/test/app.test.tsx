import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import StatusBadge from '../components/StatusBadge'
import { parseFilename } from '../services/reports'

describe('StatusBadge', () => {
  it('renders the status label', () => {
    render(<StatusBadge status="HR Interview" />)
    expect(screen.getByText('HR Interview')).toBeInTheDocument()
  })
})

describe('parseFilename', () => {
  it('reads a plain filename from Content-Disposition', () => {
    expect(
      parseFilename('attachment; filename="Laporan_Lamaran_User_20260101.xlsx"'),
    ).toBe('Laporan_Lamaran_User_20260101.xlsx')
  })

  it('prefers the RFC 5987 UTF-8 filename', () => {
    expect(
      parseFilename(
        "attachment; filename=\"fallback.pdf\"; filename*=UTF-8''Laporan%20Lamaran.pdf",
      ),
    ).toBe('Laporan Lamaran.pdf')
  })

  it('returns null when the header is missing', () => {
    expect(parseFilename(undefined)).toBeNull()
  })
})
