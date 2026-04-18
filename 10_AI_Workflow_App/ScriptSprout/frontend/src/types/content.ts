/**
 * Represent an author content list row.
 */
export type ContentListItem = {
  id: number
  author_id: number
  status: string
  genre: string | null
  subject: string | null
  title: string | null
  prompt_preview: string
  has_thumbnail: boolean
  has_audio: boolean
  guardrails_enabled: boolean
  guardrails_max_loops: number
  created_at: string
  updated_at: string
}

/**
 * Represent paginated content list response.
 */
export type ContentListPage = {
  items: ContentListItem[]
  total: number
  limit: number
  offset: number
}

/**
 * Represent full content detail payload for owned rows.
 */
export type ContentItemDetail = {
  id: number
  author_id: number
  source_prompt: string
  subject: string | null
  genre: string | null
  age_group: string | null
  video_length_minutes: number | null
  target_word_count: number | null
  title: string | null
  description: string | null
  synopsis: string | null
  story_text: string | null
  status: string
  guardrails_enabled: boolean
  guardrails_max_loops: number
  created_at: string
  updated_at: string
  has_thumbnail: boolean
  has_audio: boolean
  thumbnail_mime_type: string | null
  audio_mime_type: string | null
  audio_voice: string | null
  audio_generated_at: string | null
}

/**
 * Represent step enum for approve and regenerate actions.
 */
export type DraftStep = 'synopsis' | 'title' | 'description'
