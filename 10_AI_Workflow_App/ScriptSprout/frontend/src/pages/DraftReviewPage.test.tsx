import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { DraftReviewPage } from './DraftReviewPage'

/**
 * Build a JSON response object for fetch mocks.
 *
 * Args:
 *   body: Serializable JSON payload.
 *   init: Optional response metadata.
 *
 * Returns:
 *   Response with JSON body.
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

describe('DraftReviewPage', () => {
  it('loads list and selected detail', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input) => {
      const url = String(input)
      if (url.includes('/api/content/?')) {
        return jsonResponse({
          items: [
            {
              id: 7,
              author_id: 1,
              status: 'draft',
              genre: 'fantasy',
              subject: 'fox',
              title: null,
              prompt_preview: 'A fox prompt',
              has_thumbnail: false,
              has_audio: false,
              guardrails_enabled: true,
              guardrails_max_loops: 3,
              created_at: '2026-01-01T00:00:00Z',
              updated_at: '2026-01-01T00:00:00Z',
            },
          ],
          total: 1,
          limit: 50,
          offset: 0,
        })
      }
      if (url.endsWith('/api/content/7')) {
        return jsonResponse({
          id: 7,
          author_id: 1,
          source_prompt: 'A fox prompt',
          subject: 'fox',
          genre: 'fantasy',
          age_group: null,
          video_length_minutes: 10,
          target_word_count: null,
          title: null,
          description: null,
          synopsis: 'A shy fox sings.',
          story_text: null,
          status: 'synopsis_generated',
          guardrails_enabled: true,
          guardrails_max_loops: 3,
          created_at: '2026-01-01T00:00:00Z',
          updated_at: '2026-01-01T00:00:00Z',
          has_thumbnail: false,
          has_audio: false,
          thumbnail_mime_type: null,
          audio_mime_type: null,
          audio_voice: null,
          audio_generated_at: null,
        })
      }
      return jsonResponse({ detail: 'Unexpected route' }, { status: 404 })
    })

    render(
      <MemoryRouter>
        <DraftReviewPage />
      </MemoryRouter>,
    )

    expect(await screen.findByTestId('draft-detail')).toBeInTheDocument()
    expect(screen.getByText(/A shy fox sings/)).toBeInTheDocument()
  })

  it('runs generate synopsis action and refreshes detail', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch')
    let detailCount = 0
    fetchMock.mockImplementation(async (input, init) => {
      const url = String(input)
      if (url.includes('/api/content/?')) {
        return jsonResponse({
          items: [
            {
              id: 9,
              author_id: 1,
              status: 'draft',
              genre: 'fantasy',
              subject: 'owl',
              title: null,
              prompt_preview: 'An owl prompt',
              has_thumbnail: false,
              has_audio: false,
              guardrails_enabled: true,
              guardrails_max_loops: 3,
              created_at: '2026-01-01T00:00:00Z',
              updated_at: '2026-01-01T00:00:00Z',
            },
          ],
          total: 1,
          limit: 50,
          offset: 0,
        })
      }
      if (url.endsWith('/api/content/9/generate-synopsis') && init?.method === 'POST') {
        return jsonResponse({
          content_id: 9,
          synopsis: 'Generated synopsis',
          status: 'synopsis_generated',
          attempts_used: 1,
          openai_response_id: 'resp_9',
        })
      }
      if (url.endsWith('/api/content/9')) {
        detailCount += 1
        return jsonResponse({
          id: 9,
          author_id: 1,
          source_prompt: 'An owl prompt',
          subject: 'owl',
          genre: 'fantasy',
          age_group: null,
          video_length_minutes: 10,
          target_word_count: null,
          title: null,
          description: null,
          synopsis: detailCount > 1 ? 'Generated synopsis' : '(old)',
          story_text: null,
          status: 'synopsis_generated',
          guardrails_enabled: true,
          guardrails_max_loops: 3,
          created_at: '2026-01-01T00:00:00Z',
          updated_at: '2026-01-01T00:00:00Z',
          has_thumbnail: false,
          has_audio: false,
          thumbnail_mime_type: null,
          audio_mime_type: null,
          audio_voice: null,
          audio_generated_at: null,
        })
      }
      return jsonResponse({ detail: 'Unexpected route' }, { status: 404 })
    })

    render(
      <MemoryRouter>
        <DraftReviewPage />
      </MemoryRouter>,
    )

    expect(await screen.findByTestId('draft-detail')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Generate synopsis' }))

    await waitFor(() => {
      expect(screen.getByText(/Generated synopsis/)).toBeInTheDocument()
    })
  })

  it('honors contentId query parameter when selecting initial row', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input) => {
      const url = String(input)
      if (url.includes('/api/content/?')) {
        return jsonResponse({
          items: [
            {
              id: 5,
              author_id: 1,
              status: 'draft',
              genre: 'fantasy',
              subject: 'fox',
              title: null,
              prompt_preview: 'A fox prompt',
              has_thumbnail: false,
              has_audio: false,
              guardrails_enabled: true,
              guardrails_max_loops: 3,
              created_at: '2026-01-01T00:00:00Z',
              updated_at: '2026-01-01T00:00:00Z',
            },
            {
              id: 6,
              author_id: 1,
              status: 'draft',
              genre: 'mystery',
              subject: 'owl',
              title: null,
              prompt_preview: 'An owl prompt',
              has_thumbnail: false,
              has_audio: false,
              guardrails_enabled: true,
              guardrails_max_loops: 3,
              created_at: '2026-01-01T00:00:00Z',
              updated_at: '2026-01-01T00:00:00Z',
            },
          ],
          total: 2,
          limit: 50,
          offset: 0,
        })
      }
      if (url.endsWith('/api/content/6')) {
        return jsonResponse({
          id: 6,
          author_id: 1,
          source_prompt: 'An owl prompt',
          subject: 'owl',
          genre: 'mystery',
          age_group: null,
          video_length_minutes: 10,
          target_word_count: null,
          title: null,
          description: null,
          synopsis: 'Selected by query string',
          story_text: null,
          status: 'synopsis_generated',
          guardrails_enabled: true,
          guardrails_max_loops: 3,
          created_at: '2026-01-01T00:00:00Z',
          updated_at: '2026-01-01T00:00:00Z',
          has_thumbnail: false,
          has_audio: false,
          thumbnail_mime_type: null,
          audio_mime_type: null,
          audio_voice: null,
          audio_generated_at: null,
        })
      }
      return jsonResponse({ detail: 'Unexpected route' }, { status: 404 })
    })

    render(
      <MemoryRouter initialEntries={['/draft-review?contentId=6']}>
        <DraftReviewPage />
      </MemoryRouter>,
    )

    expect(await screen.findByTestId('draft-detail')).toBeInTheDocument()
    expect(screen.getByText(/Selected by query string/)).toBeInTheDocument()
  })

  it('falls back to first row when query contentId is not present', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input) => {
      const url = String(input)
      if (url.includes('/api/content/?')) {
        return jsonResponse({
          items: [
            {
              id: 12,
              author_id: 1,
              status: 'draft',
              genre: 'fantasy',
              subject: 'fox',
              title: null,
              prompt_preview: 'A fox prompt',
              has_thumbnail: false,
              has_audio: false,
              guardrails_enabled: true,
              guardrails_max_loops: 3,
              created_at: '2026-01-01T00:00:00Z',
              updated_at: '2026-01-01T00:00:00Z',
            },
            {
              id: 13,
              author_id: 1,
              status: 'draft',
              genre: 'mystery',
              subject: 'owl',
              title: null,
              prompt_preview: 'An owl prompt',
              has_thumbnail: false,
              has_audio: false,
              guardrails_enabled: true,
              guardrails_max_loops: 3,
              created_at: '2026-01-01T00:00:00Z',
              updated_at: '2026-01-01T00:00:00Z',
            },
          ],
          total: 2,
          limit: 50,
          offset: 0,
        })
      }
      if (url.endsWith('/api/content/12')) {
        return jsonResponse({
          id: 12,
          author_id: 1,
          source_prompt: 'A fox prompt',
          subject: 'fox',
          genre: 'fantasy',
          age_group: null,
          video_length_minutes: 10,
          target_word_count: null,
          title: null,
          description: null,
          synopsis: 'First row selected fallback',
          story_text: null,
          status: 'synopsis_generated',
          guardrails_enabled: true,
          guardrails_max_loops: 3,
          created_at: '2026-01-01T00:00:00Z',
          updated_at: '2026-01-01T00:00:00Z',
          has_thumbnail: false,
          has_audio: false,
          thumbnail_mime_type: null,
          audio_mime_type: null,
          audio_voice: null,
          audio_generated_at: null,
        })
      }
      return jsonResponse({ detail: 'Unexpected route' }, { status: 404 })
    })

    render(
      <MemoryRouter initialEntries={['/draft-review?contentId=999']}>
        <DraftReviewPage />
      </MemoryRouter>,
    )

    expect(await screen.findByTestId('draft-detail')).toBeInTheDocument()
    expect(screen.getByText(/First row selected fallback/)).toBeInTheDocument()
  })
})
