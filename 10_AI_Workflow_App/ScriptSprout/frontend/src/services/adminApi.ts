import { ApiError } from './authApi'
import type { AdminMetricsResponse, AdminNlpQueryResponse } from '../types/admin'

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
 * @returns Result generated for the caller.
 */
async function adminRequest(path: string): Promise<Response> {
  const response = await fetch(path, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
  })
  if (response.ok) {
    return response
  }
  const payload = await readJson(response)
  const detail = typeof payload?.detail === 'string' ? payload.detail : response.statusText
  throw new ApiError(detail || 'Admin request failed', response.status)
}

/**
 * Execute the function's primary application behavior.
 *
 * @param path API path fragment used to compose a request URL.
 * @param body Validated request payload.
 * @returns Result generated for the caller.
 */
async function adminRequestWithBody(path: string, body: Record<string, unknown>): Promise<Response> {
  const response = await fetch(path, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (response.ok) {
    return response
  }
  const payload = await readJson(response)
  const detail = typeof payload?.detail === 'string' ? payload.detail : response.statusText
  throw new ApiError(detail || 'Admin request failed', response.status)
}

/**
 * Retrieve data needed for this operation.
 */
export async function getAdminMetrics(params?: {
  start?: string | null
  end?: string | null
}): Promise<AdminMetricsResponse> {
  const query = new URLSearchParams()
  if (params?.start) {
    query.set('start', params.start)
  }
  if (params?.end) {
    query.set('end', params.end)
  }
  const suffix = query.toString()
  const response = await adminRequest(`/api/admin/metrics${suffix ? `?${suffix}` : ''}`)
  return (await response.json()) as AdminMetricsResponse
}

/**
 * Execute the workflow and return its result.
 *
 * @param query Natural-language query string.
 * @returns Result generated for the caller.
 */
export async function runAdminNlpQuery(query: string): Promise<AdminNlpQueryResponse> {
  const response = await adminRequestWithBody('/api/admin/nlp-query', { query })
  return (await response.json()) as AdminNlpQueryResponse
}
