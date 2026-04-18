import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { StoryMediaPage } from './StoryMediaPage'

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

describe('StoryMediaPage', () => {
  it('loads selected detail and shows media state', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input) => {
      const url = String(input)
      if (url.includes('/api/content/?')) {
        return jsonResponse({
          items: [
            {
              id: 21,
              author_id: 1,
              status: 'guardrails_passed',
              genre: 'fantasy',
              subject: 'fox',
              title: 'Fox story',
              prompt_preview: 'A fox prompt',
              has_thumbnail: true,
              has_audio: true,
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
      if (url.endsWith('/api/content/21')) {
        return jsonResponse({
          id: 21,
          author_id: 1,
          source_prompt: 'A fox prompt',
          subject: 'fox',
          genre: 'fantasy',
          age_group: 'kids',
          video_length_minutes: 10,
          target_word_count: null,
          title: 'Fox story',
          description: 'Cozy fox description',
          synopsis: 'Synopsis',
          story_text: 'Final story text',
          status: 'guardrails_passed',
          guardrails_enabled: true,
          guardrails_max_loops: 3,
          created_at: '2026-01-01T00:00:00Z',
          updated_at: '2026-01-01T00:00:00Z',
          has_thumbnail: true,
          has_audio: true,
          thumbnail_mime_type: 'image/png',
          audio_mime_type: 'audio/mpeg',
          audio_voice: 'alloy',
          audio_generated_at: '2026-01-01T00:00:00Z',
        })
      }
      return jsonResponse({ detail: 'Unexpected route' }, { status: 404 })
    })

    render(
      <MemoryRouter>
        <StoryMediaPage />
      </MemoryRouter>,
    )

    expect(await screen.findByTestId('story-media-detail')).toBeInTheDocument()
    expect(screen.getByText(/Final story text/)).toBeInTheDocument()
    expect(screen.getByText(/Has thumbnail:/)).toBeInTheDocument()
    expect(screen.getByText(/Has audio:/)).toBeInTheDocument()
  })

  it('runs generate story action and refreshes detail', async () => {
    let detailCount = 0
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input, init) => {
      const url = String(input)
      if (url.includes('/api/content/?')) {
        return jsonResponse({
          items: [
            {
              id: 22,
              author_id: 1,
              status: 'description_approved',
              genre: 'fantasy',
              subject: 'owl',
              title: 'Owl story',
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
      if (url.endsWith('/api/content/22/generate-story') && init?.method === 'POST') {
        return jsonResponse({
          content_id: 22,
          story_text: 'Generated story',
          status: 'guardrails_passed',
          story_attempts_used: 1,
          guardrails_attempts_used: 1,
          openai_story_response_id: 'resp_story',
          openai_guardrails_response_id: 'resp_guard',
        })
      }
      if (url.endsWith('/api/content/22')) {
        detailCount += 1
        return jsonResponse({
          id: 22,
          author_id: 1,
          source_prompt: 'An owl prompt',
          subject: 'owl',
          genre: 'fantasy',
          age_group: 'kids',
          video_length_minutes: 10,
          target_word_count: null,
          title: 'Owl story',
          description: 'Desc',
          synopsis: 'Synopsis',
          story_text: detailCount > 1 ? 'Generated story' : null,
          status: detailCount > 1 ? 'guardrails_passed' : 'description_approved',
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
        <StoryMediaPage />
      </MemoryRouter>,
    )

    expect(await screen.findByTestId('story-media-detail')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Generate story' }))

    await waitFor(() => {
      expect(screen.getByText(/Generated story/)).toBeInTheDocument()
    })
  })

  it('shows no-media placeholders when thumbnail/audio are unavailable', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input) => {
      const url = String(input)
      if (url.includes('/api/content/?')) {
        return jsonResponse({
          items: [
            {
              id: 23,
              author_id: 1,
              status: 'description_approved',
              genre: 'fantasy',
              subject: 'cat',
              title: 'Cat story',
              prompt_preview: 'A cat prompt',
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
      if (url.endsWith('/api/content/23')) {
        return jsonResponse({
          id: 23,
          author_id: 1,
          source_prompt: 'A cat prompt',
          subject: 'cat',
          genre: 'fantasy',
          age_group: 'kids',
          video_length_minutes: 10,
          target_word_count: null,
          title: 'Cat story',
          description: 'Desc',
          synopsis: 'Synopsis',
          story_text: 'Story text',
          status: 'description_approved',
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
        <StoryMediaPage />
      </MemoryRouter>,
    )

    expect(await screen.findByTestId('story-media-detail')).toBeInTheDocument()
    expect(screen.getByText('No thumbnail yet.')).toBeInTheDocument()
    expect(screen.getByText('No audio yet.')).toBeInTheDocument()
  })

  it('shows API error when generate thumbnail fails', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input, init) => {
      const url = String(input)
      if (url.includes('/api/content/?')) {
        return jsonResponse({
          items: [
            {
              id: 24,
              author_id: 1,
              status: 'guardrails_passed',
              genre: 'fantasy',
              subject: 'fox',
              title: 'Fox story',
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
      if (url.endsWith('/api/content/24')) {
        return jsonResponse({
          id: 24,
          author_id: 1,
          source_prompt: 'A fox prompt',
          subject: 'fox',
          genre: 'fantasy',
          age_group: 'kids',
          video_length_minutes: 10,
          target_word_count: null,
          title: 'Fox story',
          description: 'Desc',
          synopsis: 'Synopsis',
          story_text: 'Story text',
          status: 'guardrails_passed',
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
      if (url.endsWith('/api/content/24/generate-thumbnail') && init?.method === 'POST') {
        return jsonResponse({ detail: 'Thumbnail failed' }, { status: 500, statusText: 'Server Error' })
      }
      return jsonResponse({ detail: 'Unexpected route' }, { status: 404 })
    })

    render(
      <MemoryRouter>
        <StoryMediaPage />
      </MemoryRouter>,
    )

    expect(await screen.findByTestId('story-media-detail')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Generate thumbnail' }))

    await waitFor(() => {
      expect(screen.getByText('Thumbnail failed')).toBeInTheDocument()
    })
  })
})
