import { useState } from 'react'
import { ApiError } from '../services/authApi'
import { runAdminNlpQuery } from '../services/adminApi'
import type { AdminNlpQueryResponse } from '../types/admin'

/**
 * Execute the function's primary application behavior.
 *
 * @param error Error object captured from a failed async/API operation.
 * @returns Result generated for the caller.
 */
function adminNlpErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 401) {
      return 'Your session expired. Please login again.'
    }
    if (error.status === 403) {
      return 'Only admins can use admin NLP query.'
    }
    return error.message
  }
  return 'Could not run admin NLP query.'
}

/**
 * Execute the function's primary application behavior.
 */
export function AdminNlpQueryPage() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<AdminNlpQueryResponse | null>(null)

  /**
   * Execute the function's primary application behavior.
   */
  async function onSubmit() {
    if (!query.trim() || loading) {
      return
    }
    setLoading(true)
    setError(null)
    try {
      const payload = await runAdminNlpQuery(query.trim())
      setResult(payload)
    } catch (error_: unknown) {
      setError(adminNlpErrorMessage(error_))
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <h2>Admin NLP query</h2>
      <p className="muted">
        Ask a natural-language admin question and view the composed metrics and/or
        semantic search response.
      </p>

      <form
        className="auth-form"
        onSubmit={(event) => {
          event.preventDefault()
          void onSubmit()
        }}
      >
        <label>
          Query
          <textarea
            name="query"
            rows={4}
            placeholder="How many stories this week by genre, and show similar fox stories?"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            required
          />
        </label>
        <button type="submit" disabled={loading || !query.trim()}>
          {loading ? 'Running…' : 'Run query'}
        </button>
      </form>

      {error && <p className="err">{error}</p>}

      {result && (
        <section className="group" data-testid="admin-nlp-result">
          <h3>Plan summary</h3>
          <p className="muted">{result.plan_summary}</p>
          <p className="muted">Parse attempts: {result.parse_attempts_used}</p>

          {result.metrics && (
            <section className="group">
              <h3>Metrics snapshot</h3>
              <ul className="result-list">
                <li>
                  <strong>Window:</strong> {result.metrics.window.start} → {result.metrics.window.end}
                </li>
                <li>
                  <strong>Content created:</strong> {result.metrics.content.items_created}
                </li>
                <li>
                  <strong>Model calls:</strong> {result.metrics.model_calls.total}
                </li>
              </ul>
            </section>
          )}

          {result.semantic_search && (
            <section className="group">
              <h3>Semantic hits</h3>
              {result.semantic_search.items.length === 0 ? (
                <p className="muted">No semantic matches in this query scope.</p>
              ) : (
                <ul className="result-list" data-testid="semantic-hit-list">
                  {result.semantic_search.items.map((hit) => (
                    <li key={`${hit.content.id}-${hit.distance}`}>
                      <strong>#{hit.content.id}</strong> {hit.content.title ?? '(untitled)'} —{' '}
                      {hit.content.prompt_preview}
                    </li>
                  ))}
                </ul>
              )}
            </section>
          )}
        </section>
      )}
    </>
  )
}
