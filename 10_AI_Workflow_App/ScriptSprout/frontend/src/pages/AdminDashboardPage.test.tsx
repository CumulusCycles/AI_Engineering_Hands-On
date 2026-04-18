import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { AdminDashboardPage } from './AdminDashboardPage'

/**
 * Build a JSON response object for fetch mocks.
 *
 * Args:
 *   body: Serializable payload.
 *   init: Optional response metadata.
 *
 * Returns:
 *   Response with JSON payload.
 */
function jsonResponse(body: unknown, init?: ResponseInit): Response {
  return new Response(JSON.stringify(body), {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
}

afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
})

describe('AdminDashboardPage', () => {
  it('loads metrics and renders cards/tables', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      jsonResponse({
        window: {
          start: '2026-03-01T00:00:00Z',
          end: '2026-03-26T00:00:00Z',
          used_default_window: true,
        },
        content: {
          items_created: 12,
          by_status: [{ label: 'draft', count: 4 }],
          by_genre: [{ label: 'fantasy', count: 6 }],
        },
        model_calls: {
          total: 18,
          success_count: 17,
          failure_count: 1,
          avg_latency_ms: 802.4,
          total_token_input: 1200,
          total_token_output: 4400,
          by_purpose: [{ label: 'extract_story_parameters', count: 5 }],
          by_model: [{ label: 'gpt-4.1-mini', count: 10 }],
        },
        generation_runs: {
          total: 6,
          by_status: [{ label: 'guardrails_passed', count: 5 }],
          avg_story_attempts: 1.2,
          avg_guardrails_attempts: 1.1,
        },
        guardrails: {
          events_total: 7,
          passed_count: 6,
          failed_count: 1,
        },
        audit: {
          events_total: 9,
          by_event_type: [{ label: 'approve_synopsis', count: 3 }],
        },
      }),
    )

    render(
      <MemoryRouter>
        <AdminDashboardPage />
      </MemoryRouter>,
    )

    expect(await screen.findByTestId('metrics-cards')).toBeInTheDocument()
    expect(screen.getByText('12')).toBeInTheDocument()
    expect(screen.getByText('extract_story_parameters')).toBeInTheDocument()
  })

  it('passes start/end query values when refreshing metrics', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch')
    fetchMock.mockResolvedValue(
      jsonResponse({
        window: { start: '2026-03-01T00:00:00Z', end: '2026-03-26T00:00:00Z', used_default_window: false },
        content: { items_created: 0, by_status: [], by_genre: [] },
        model_calls: {
          total: 0,
          success_count: 0,
          failure_count: 0,
          avg_latency_ms: null,
          total_token_input: null,
          total_token_output: null,
          by_purpose: [],
          by_model: [],
        },
        generation_runs: { total: 0, by_status: [], avg_story_attempts: null, avg_guardrails_attempts: null },
        guardrails: { events_total: 0, passed_count: 0, failed_count: 0 },
        audit: { events_total: 0, by_event_type: [] },
      }),
    )

    render(
      <MemoryRouter>
        <AdminDashboardPage />
      </MemoryRouter>,
    )
    await screen.findByTestId('metrics-window')

    fireEvent.change(screen.getByLabelText('Start (ISO 8601)'), {
      target: { value: '2026-03-01T00:00:00Z' },
    })
    fireEvent.change(screen.getByLabelText('End (ISO 8601)'), {
      target: { value: '2026-03-20T23:59:59Z' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Refresh metrics' }))

    await waitFor(() => {
      expect(fetchMock).toHaveBeenLastCalledWith(
        '/api/admin/metrics?start=2026-03-01T00%3A00%3A00Z&end=2026-03-20T23%3A59%3A59Z',
        expect.objectContaining({
          credentials: 'include',
        }),
      )
    })
  })
})
