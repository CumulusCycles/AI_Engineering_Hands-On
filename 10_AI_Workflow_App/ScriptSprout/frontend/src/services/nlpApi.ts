import { ApiError } from './authApi'
import type {
  ExtractStoryParametersRequest,
  StoryParametersExtractResponse,
} from '../types/nlp'

/**
 * Execute the function's primary application behavior.
 *
 * @param response Outgoing HTTP response to mutate headers/cookies.
 * @returns Result generated for the caller.
 */
async function readJson(
  response: Response,
): Promise<Record<string, unknown> | undefined> {
  const text = await response.text()
  if (!text) {
    return undefined
  }
  return JSON.parse(text) as Record<string, unknown>
}

/**
 * Execute the function's primary application behavior.
 *
 * @param body Validated request payload.
 * @returns Result generated for the caller.
 */
export async function extractStoryParameters(
  body: ExtractStoryParametersRequest,
): Promise<StoryParametersExtractResponse> {
  const response = await fetch('/api/nlp/extract-story-parameters', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    const payload = await readJson(response)
    const detail = typeof payload?.detail === 'string' ? payload.detail : response.statusText
    throw new ApiError(detail || 'NLP extraction failed', response.status)
  }

  return (await response.json()) as StoryParametersExtractResponse
}
