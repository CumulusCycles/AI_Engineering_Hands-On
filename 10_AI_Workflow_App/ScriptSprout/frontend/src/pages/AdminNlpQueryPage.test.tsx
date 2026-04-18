import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { AdminNlpQueryPage } from './AdminNlpQueryPage'

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

function deferredResponse() {
  let resolve!: (value: Response) => void
  const promise = new Promise<Response>((r) => {
    resolve = r
  })
  return { promise, resolve }
}

afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
})

describe('AdminNlpQueryPage', () => {
  it('renders mixed metrics and semantic search results', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      jsonResponse({
        query: 'How many stories this week?',
        plan_summary: 'Run metrics and semantic search.',
        parse_attempts_used: 1,
        metrics: {
          window: {
            start: '2026-03-01T00:00:00Z',
            end: '2026-03-26T00:00:00Z',
            used_default_window: false,
          },
          content: { items_created: 9, by_status: [], by_genre: [] },
          model_calls: {
            total: 14,
            success_count: 13,
            failure_count: 1,
            avg_latency_ms: 710.5,
            total_token_input: 1000,
            total_token_output: 4000,
            by_purpose: [],
            by_model: [],
          },
          generation_runs: {
            total: 4,
            by_status: [],
            avg_story_attempts: 1.0,
            avg_guardrails_attempts: 1.0,
          },
          guardrails: { events_total: 4, passed_count: 4, failed_count: 0 },
          audit: { events_total: 6, by_event_type: [] },
        },
        semantic_search: {
          embedding_model: 'text-embedding-3-small',
          attempts_used: 1,
          items: [
            {
              distance: 0.12,
              content: {
                id: 77,
                author_id: 1,
                status: 'draft',
                genre: 'fantasy',
                subject: 'fox',
                title: 'Fox Story',
                prompt_preview: 'A fox prompt',
                has_thumbnail: false,
                has_audio: false,
                guardrails_enabled: true,
                guardrails_max_loops: 3,
                created_at: '2026-01-01T00:00:00Z',
                updated_at: '2026-01-01T00:00:00Z',
              },
            },
          ],
        },
      }),
    )

    render(
      <MemoryRouter>
        <AdminNlpQueryPage />
      </MemoryRouter>,
    )

    fireEvent.change(screen.getByLabelText('Query'), {
      target: { value: 'How many stories this week?' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Run query' }))

    expect(await screen.findByTestId('admin-nlp-result')).toBeInTheDocument()
    expect(screen.getByText(/Run metrics and semantic search/)).toBeInTheDocument()
    expect(screen.getByTestId('semantic-hit-list')).toHaveTextContent('Fox Story')
  })

  it('shows user-facing API error messages', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      jsonResponse({ detail: 'NLP query unavailable' }, { status: 503 }),
    )

    render(
      <MemoryRouter>
        <AdminNlpQueryPage />
      </MemoryRouter>,
    )

    fireEvent.change(screen.getByLabelText('Query'), {
      target: { value: 'How many stories this week?' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Run query' }))

    await waitFor(() => {
      expect(screen.getByText('NLP query unavailable')).toBeInTheDocument()
    })
  })

  it('disables submit while query request is in flight', async () => {
    const pending = deferredResponse()
    vi.spyOn(globalThis, 'fetch').mockReturnValue(pending.promise)

    render(
      <MemoryRouter>
        <AdminNlpQueryPage />
      </MemoryRouter>,
    )

    fireEvent.change(screen.getByLabelText('Query'), {
      target: { value: 'How many stories this week?' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Run query' }))

    expect(screen.getByRole('button', { name: 'Running…' })).toBeDisabled()

    pending.resolve(
      jsonResponse({
        query: 'How many stories this week?',
        plan_summary: 'metrics only',
        parse_attempts_used: 1,
        metrics: {
          window: {
            start: '2026-03-01T00:00:00Z',
            end: '2026-03-26T00:00:00Z',
            used_default_window: false,
          },
          content: { items_created: 1, by_status: [], by_genre: [] },
          model_calls: {
            total: 1,
            success_count: 1,
            failure_count: 0,
            avg_latency_ms: null,
            total_token_input: null,
            total_token_output: null,
            by_purpose: [],
            by_model: [],
          },
          generation_runs: {
            total: 0,
            by_status: [],
            avg_story_attempts: null,
            avg_guardrails_attempts: null,
          },
          guardrails: { events_total: 0, passed_count: 0, failed_count: 0 },
          audit: { events_total: 0, by_event_type: [] },
        },
        semantic_search: null,
      }),
    )

    expect(await screen.findByTestId('admin-nlp-result')).toBeInTheDocument()
  })
})
