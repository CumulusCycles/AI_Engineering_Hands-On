/**
 * Represent a single follow-up question for a missing extracted field.
 */
export type MissingFieldFollowUp = {
  field: string
  question: string
  input_kind: 'text' | 'number' | 'single_select'
  guidance: string | null
  suggested_options: string[] | null
}

/**
 * Represent the NLP extract request payload.
 */
export type ExtractStoryParametersRequest = {
  prompt: string
}

/**
 * Represent the NLP extract response payload.
 */
export type StoryParametersExtractResponse = {
  subject: string | null
  genre: string | null
  age_group: string | null
  video_length_minutes: number | null
  target_word_count: number | null
  missing_fields: string[]
  is_complete: boolean
  follow_up: MissingFieldFollowUp[]
  attempts_used: number
  openai_response_id: string | null
}
