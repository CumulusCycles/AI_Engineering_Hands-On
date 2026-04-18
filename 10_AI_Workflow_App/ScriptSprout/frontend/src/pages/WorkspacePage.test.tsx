import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { WorkspacePage } from './WorkspacePage'

/**
 * Build a JSON response object for fetch mocks.
 *
 * Args:
 *   body: Serializable payload for response JSON.
 *   init: Optional response metadata.
 *
 * Returns:
 *   Response object with JSON body.
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
  window.sessionStorage.clear()
  cleanup()
  vi.restoreAllMocks()
})

describe('WorkspacePage', () => {
  it('renders extraction result and follow-up questions', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      jsonResponse({
        subject: 'A shy fox learning to sing',
        genre: 'fantasy',
        age_group: null,
        video_length_minutes: 12,
        target_word_count: null,
        missing_fields: ['age_group'],
        is_complete: false,
        follow_up: [
          {
            field: 'age_group',
            question: 'Who is the target audience?',
            input_kind: 'single_select',
            guidance: null,
            suggested_options: ['kids', 'tween'],
          },
        ],
        attempts_used: 1,
        openai_response_id: 'resp_123',
      }),
    )

    render(
      <MemoryRouter>
        <WorkspacePage />
      </MemoryRouter>,
    )

    fireEvent.change(screen.getByLabelText('Prompt'), {
      target: { value: 'A 12-minute fantasy story about a shy fox.' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Extract parameters' }))

    expect(await screen.findByTestId('extract-result')).toBeInTheDocument()
    expect(screen.getByText(/A shy fox learning to sing/)).toBeInTheDocument()
    expect(screen.getByTestId('follow-up-list')).toHaveTextContent('Who is the target audience?')
  })

  it('shows API failures as user-facing messages', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      jsonResponse({ detail: 'Service unavailable' }, { status: 503 }),
    )

    render(
      <MemoryRouter>
        <WorkspacePage />
      </MemoryRouter>,
    )

    fireEvent.change(screen.getByLabelText('Prompt'), {
      target: { value: 'A short story prompt.' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Extract parameters' }))

    await waitFor(() => {
      expect(
        screen.getByText('NLP service is unavailable. Check OPENAI_API_KEY and retry.'),
      ).toBeInTheDocument()
    })
  })

  it('creates a draft from complete extraction and navigates to draft review', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input, init) => {
      const url = String(input)
      if (url.endsWith('/api/nlp/extract-story-parameters') && init?.method === 'POST') {
        return jsonResponse({
          subject: 'Shy fox learns to sing',
          genre: 'fantasy',
          age_group: 'kids',
          video_length_minutes: 10,
          target_word_count: 750,
          missing_fields: [],
          is_complete: true,
          follow_up: [],
          attempts_used: 1,
          openai_response_id: 'resp_123',
        })
      }
      if (url.endsWith('/api/content/') && init?.method === 'POST') {
        return jsonResponse({
          id: 44,
          author_id: 1,
          source_prompt: 'A complete prompt',
          subject: 'Shy fox learns to sing',
          genre: 'fantasy',
          age_group: 'kids',
          video_length_minutes: 10,
          target_word_count: 750,
          title: null,
          description: null,
          synopsis: null,
          story_text: null,
          status: 'draft',
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
      <MemoryRouter initialEntries={['/workspace']}>
        <Routes>
          <Route path="/workspace" element={<WorkspacePage />} />
          <Route path="/draft-review" element={<h2>Draft review page</h2>} />
        </Routes>
      </MemoryRouter>,
    )

    fireEvent.change(screen.getByLabelText('Prompt'), {
      target: { value: 'A complete prompt' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Extract parameters' }))

    expect(await screen.findByRole('button', { name: 'Create content draft' })).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Create content draft' }))

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Draft review page' })).toBeInTheDocument()
    })
  })

  it('does not show create-draft button when extraction is incomplete', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      jsonResponse({
        subject: 'Shy fox learns to sing',
        genre: 'fantasy',
        age_group: null,
        video_length_minutes: 10,
        target_word_count: null,
        missing_fields: ['age_group'],
        is_complete: false,
        follow_up: [
          {
            field: 'age_group',
            question: 'Who is the target audience?',
            input_kind: 'single_select',
            guidance: null,
            suggested_options: ['kids', 'tween'],
          },
        ],
        attempts_used: 1,
        openai_response_id: 'resp_incomplete',
      }),
    )

    render(
      <MemoryRouter>
        <WorkspacePage />
      </MemoryRouter>,
    )

    fireEvent.change(screen.getByLabelText('Prompt'), {
      target: { value: 'A fantasy fox story' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Extract parameters' }))

    expect(await screen.findByTestId('extract-result')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Create content draft' })).toBeNull()
  })

  it('shows create-draft API failures as user-facing messages', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input, init) => {
      const url = String(input)
      if (url.endsWith('/api/nlp/extract-story-parameters') && init?.method === 'POST') {
        return jsonResponse({
          subject: 'Shy fox learns to sing',
          genre: 'fantasy',
          age_group: 'kids',
          video_length_minutes: 10,
          target_word_count: 750,
          missing_fields: [],
          is_complete: true,
          follow_up: [],
          attempts_used: 1,
          openai_response_id: 'resp_ok',
        })
      }
      if (url.endsWith('/api/content/') && init?.method === 'POST') {
        return jsonResponse({ detail: 'Create failed' }, { status: 500, statusText: 'Server Error' })
      }
      return jsonResponse({ detail: 'Unexpected route' }, { status: 404 })
    })

    render(
      <MemoryRouter>
        <WorkspacePage />
      </MemoryRouter>,
    )

    fireEvent.change(screen.getByLabelText('Prompt'), {
      target: { value: 'A complete prompt' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Extract parameters' }))
    fireEvent.click(await screen.findByRole('button', { name: 'Create content draft' }))

    await waitFor(() => {
      expect(screen.getByText('Create failed')).toBeInTheDocument()
    })
  })

  it('restores prompt and extraction result from session storage', async () => {
    window.sessionStorage.setItem(
      'scriptsprout.workspace.last',
      JSON.stringify({
        prompt: 'Persisted prompt text',
        result: {
          subject: 'Persisted subject',
          genre: 'fantasy',
          age_group: 'kids',
          video_length_minutes: 8,
          target_word_count: 600,
          missing_fields: [],
          is_complete: true,
          follow_up: [],
          attempts_used: 1,
          openai_response_id: 'resp_saved',
        },
      }),
    )

    render(
      <MemoryRouter>
        <WorkspacePage />
      </MemoryRouter>,
    )

    expect(screen.getByLabelText('Prompt')).toHaveValue('Persisted prompt text')
    expect(screen.getByTestId('extract-result')).toHaveTextContent('Persisted subject')
    expect(screen.getByRole('button', { name: 'Create content draft' })).toBeInTheDocument()
  })

  it('disables extract submit while request is in flight', async () => {
    const pending = deferredResponse()
    vi.spyOn(globalThis, 'fetch').mockReturnValue(pending.promise)

    render(
      <MemoryRouter>
        <WorkspacePage />
      </MemoryRouter>,
    )

    fireEvent.change(screen.getByLabelText('Prompt'), {
      target: { value: 'A pending prompt' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Extract parameters' }))

    expect(screen.getByRole('button', { name: 'Extracting…' })).toBeDisabled()

    pending.resolve(
      jsonResponse({
        subject: 'Done',
        genre: 'fantasy',
        age_group: 'kids',
        video_length_minutes: 10,
        target_word_count: 700,
        missing_fields: [],
        is_complete: true,
        follow_up: [],
        attempts_used: 1,
        openai_response_id: 'resp_done',
      }),
    )

    expect(await screen.findByTestId('extract-result')).toBeInTheDocument()
  })
})
