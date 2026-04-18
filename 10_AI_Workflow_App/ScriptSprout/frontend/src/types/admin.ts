import type { ContentListItem } from './content'

/**
 * Represent a metrics label-count grouping row.
 */
export type LabelCountBucket = {
  label: string
  count: number
}

/**
 * Represent admin metrics response payload from `/api/admin/metrics`.
 */
export type AdminMetricsResponse = {
  window: {
    start: string
    end: string
    used_default_window: boolean
  }
  content: {
    items_created: number
    by_status: LabelCountBucket[]
    by_genre: LabelCountBucket[]
  }
  model_calls: {
    total: number
    success_count: number
    failure_count: number
    avg_latency_ms: number | null
    total_token_input: number | null
    total_token_output: number | null
    by_purpose: LabelCountBucket[]
    by_model: LabelCountBucket[]
  }
  generation_runs: {
    total: number
    by_status: LabelCountBucket[]
    avg_story_attempts: number | null
    avg_guardrails_attempts: number | null
  }
  guardrails: {
    events_total: number
    passed_count: number
    failed_count: number
  }
  audit: {
    events_total: number
    by_event_type: LabelCountBucket[]
  }
}

/**
 * Represent one semantic search hit in admin NLP query results.
 */
export type AdminSemanticSearchHit = {
  distance: number
  content: ContentListItem
}

/**
 * Represent semantic search output included in admin NLP responses.
 */
export type AdminSemanticSearchResponse = {
  items: AdminSemanticSearchHit[]
  embedding_model: string
  attempts_used: number
}

/**
 * Represent `/api/admin/nlp-query` response payload.
 */
export type AdminNlpQueryResponse = {
  query: string
  plan_summary: string
  metrics: AdminMetricsResponse | null
  semantic_search: AdminSemanticSearchResponse | null
  parse_attempts_used: number
}
