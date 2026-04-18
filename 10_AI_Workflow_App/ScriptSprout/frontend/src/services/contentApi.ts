import { ApiError } from './authApi'
import type {
  ContentItemDetail,
  ContentListPage,
  DraftStep,
} from '../types/content'

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
 * @param path API path fragment used to compose a request URL.
 * @param init? Input value used to perform this operation.
 * @returns Result generated for the caller.
 */
async function contentRequest(path: string, init?: RequestInit): Promise<Response> {
  const response = await fetch(path, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  })
  if (response.ok) {
    return response
  }
  const payload = await readJson(response)
  const detail = typeof payload?.detail === 'string' ? payload.detail : response.statusText
  throw new ApiError(detail || 'Content request failed', response.status)
}

/**
 * Return a collection of matching records.
 * @returns Result generated for the caller.
 */
export async function listMyContent(): Promise<ContentListPage> {
  const response = await contentRequest('/api/content/?limit=50&offset=0')
  return (await response.json()) as ContentListPage
}

/**
 * Retrieve data needed for this operation.
 *
 * @param contentId Input value used to perform this operation.
 * @returns Result generated for the caller.
 */
export async function getContentItem(contentId: number): Promise<ContentItemDetail> {
  const response = await contentRequest(`/api/content/${contentId}`)
  return (await response.json()) as ContentItemDetail
}

/**
 * Create and persist a new record.
 */
export async function createContentItem(body: {
  prompt: string
  subject?: string | null
  genre?: string | null
  age_group?: string | null
  video_length_minutes?: number | null
  target_word_count?: number | null
}): Promise<ContentItemDetail> {
  const response = await contentRequest('/api/content/', {
    method: 'POST',
    body: JSON.stringify(body),
  })
  return (await response.json()) as ContentItemDetail
}

/**
 * Generate output for the requested content step.
 *
 * @param contentId Input value used to perform this operation.
 * @returns Result generated for the caller.
 */
export async function generateSynopsis(contentId: number): Promise<void> {
  await contentRequest(`/api/content/${contentId}/generate-synopsis`, { method: 'POST' })
}

/**
 * Generate output for the requested content step.
 *
 * @param contentId Input value used to perform this operation.
 * @returns Result generated for the caller.
 */
export async function generateTitle(contentId: number): Promise<void> {
  await contentRequest(`/api/content/${contentId}/generate-title`, { method: 'POST' })
}

/**
 * Generate output for the requested content step.
 *
 * @param contentId Input value used to perform this operation.
 * @returns Result generated for the caller.
 */
export async function generateDescription(contentId: number): Promise<void> {
  await contentRequest(`/api/content/${contentId}/generate-description`, { method: 'POST' })
}

/**
 * Generate output for the requested content step.
 *
 * @param contentId Input value used to perform this operation.
 * @returns Result generated for the caller.
 */
export async function generateStory(contentId: number): Promise<void> {
  await contentRequest(`/api/content/${contentId}/generate-story`, { method: 'POST' })
}

/**
 * Generate output for the requested content step.
 *
 * @param contentId Input value used to perform this operation.
 * @returns Result generated for the caller.
 */
export async function generateThumbnail(contentId: number): Promise<void> {
  await contentRequest(`/api/content/${contentId}/generate-thumbnail`, { method: 'POST' })
}

/**
 * Generate output for the requested content step.
 *
 * @param contentId Input value used to perform this operation.
 * @returns Result generated for the caller.
 */
export type TtsVoiceKey = 'female_us' | 'female_uk' | 'male_us' | 'male_uk'

export async function generateAudio(contentId: number): Promise<void> {
  await contentRequest(`/api/content/${contentId}/generate-audio`, {
    method: 'POST',
    body: JSON.stringify({}),
  })
}

/** POST generate-audio with a logical voice key (maps to OpenAI voice names on the server). */
export async function generateAudioWithVoice(
  contentId: number,
  voiceKey: TtsVoiceKey,
): Promise<void> {
  await contentRequest(`/api/content/${contentId}/generate-audio`, {
    method: 'POST',
    body: JSON.stringify({ voice_key: voiceKey }),
  })
}

/**
 * Execute the function's primary application behavior.
 *
 * @param contentId Input value used to perform this operation.
 * @param step Draft step name used for approval or regeneration.
 * @returns Result generated for the caller.
 */
export async function approveStep(contentId: number, step: DraftStep): Promise<void> {
  await contentRequest(`/api/content/${contentId}/approve-step`, {
    method: 'POST',
    body: JSON.stringify({ step }),
  })
}

/**
 * Execute the function's primary application behavior.
 *
 * @param contentId Input value used to perform this operation.
 * @param step Draft step name used for approval or regeneration.
 * @returns Result generated for the caller.
 */
export async function regenerateStep(contentId: number, step: DraftStep): Promise<void> {
  await contentRequest(`/api/content/${contentId}/regenerate-step`, {
    method: 'POST',
    body: JSON.stringify({ step }),
  })
}

/**
 * Execute the function's primary application behavior.
 *
 * @param contentId Input value used to perform this operation.
 * @returns Result generated for the caller.
 */
export function thumbnailUrl(contentId: number): string {
  return `/api/content/${contentId}/thumbnail`
}

/**
 * Execute the function's primary application behavior.
 *
 * @param contentId Input value used to perform this operation.
 * @returns Result generated for the caller.
 */
export function audioUrl(contentId: number): string {
  return `/api/content/${contentId}/audio`
}
