import { useMemo, useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import type { StoryParametersExtractResponse } from "../types/nlp";
import { ApiError } from "../services/authApi";
import { createContentItem } from "../services/contentApi";
import { extractStoryParameters } from "../services/nlpApi";

/**
 * Execute the function's primary application behavior.
 *
 * @param error Error object captured from a failed async/API operation.
 * @returns Result generated for the caller.
 */
function extractionErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 401) {
      return "Your session expired. Please login again.";
    }
    if (error.status === 403) {
      return "Only authors can use this extraction endpoint.";
    }
    if (error.status === 503) {
      return "NLP service is unavailable. Check OPENAI_API_KEY and retry.";
    }
    return error.message;
  }
  return "Could not extract story parameters.";
}

const WORKSPACE_STORAGE_KEY = "scriptsprout.workspace.last";

/**
 * Execute the function's primary application behavior.
 */
export function WorkspacePage() {
  const navigate = useNavigate();
  const [prompt, setPrompt] = useState(() => {
    const raw = window.sessionStorage.getItem(WORKSPACE_STORAGE_KEY);
    if (!raw) {
      return "";
    }
    try {
      const parsed = JSON.parse(raw) as { prompt?: string };
      return typeof parsed.prompt === "string" ? parsed.prompt : "";
    } catch {
      return "";
    }
  });
  const [submitting, setSubmitting] = useState(false);
  const [creatingDraft, setCreatingDraft] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<StoryParametersExtractResponse | null>(
    () => {
      const raw = window.sessionStorage.getItem(WORKSPACE_STORAGE_KEY);
      if (!raw) {
        return null;
      }
      try {
        const parsed = JSON.parse(raw) as {
          result?: StoryParametersExtractResponse | null;
        };
        return parsed.result ?? null;
      } catch {
        return null;
      }
    },
  );

  const canSubmit = useMemo(
    () => prompt.trim().length > 0 && !submitting,
    [prompt, submitting],
  );

  /**
   * Execute the function's primary application behavior.
   *
   * @param event Input value used to perform this operation.
   */
  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canSubmit) {
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const extracted = await extractStoryParameters({ prompt });
      setResult(extracted);
      try {
        window.sessionStorage.setItem(
          WORKSPACE_STORAGE_KEY,
          JSON.stringify({ prompt, result: extracted }),
        );
      } catch {
        /* storage full — extraction still usable in-memory */
      }
    } catch (error_: unknown) {
      setError(extractionErrorMessage(error_));
      setResult(null);
    } finally {
      setSubmitting(false);
    }
  }

  /**
   * Execute the function's primary application behavior.
   */
  async function onCreateDraft() {
    if (!result || !result.is_complete || creatingDraft || submitting) {
      return;
    }
    setCreatingDraft(true);
    setError(null);
    try {
      const created = await createContentItem({
        prompt,
        subject: result.subject,
        genre: result.genre,
        age_group: result.age_group,
        video_length_minutes: result.video_length_minutes,
        target_word_count: result.target_word_count,
      });
      navigate(`/draft-review?contentId=${created.id}`);
    } catch (error_: unknown) {
      setError(extractionErrorMessage(error_));
    } finally {
      setCreatingDraft(false);
    }
  }

  return (
    <>
      <h2>Author workspace</h2>
      <p className="muted">
        Extract story parameters from a free-form prompt and review any missing
        fields before generation.
      </p>

      <form className="auth-form" onSubmit={(event) => void onSubmit(event)}>
        <label>
          Prompt
          <textarea
            name="prompt"
            rows={5}
            placeholder="A 12-minute cozy fantasy story for kids about..."
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            required
          />
        </label>
        <button type="submit" disabled={!canSubmit}>
          {submitting ? "Extracting…" : "Extract parameters"}
        </button>
      </form>

      {error && <p className="err">{error}</p>}

      {result && (
        <section className="group" data-testid="extract-result">
          <h3>Extracted parameters</h3>
          <ul className="result-list">
            <li>
              <strong>Subject:</strong> {result.subject ?? "(missing)"}
            </li>
            <li>
              <strong>Genre:</strong> {result.genre ?? "(missing)"}
            </li>
            <li>
              <strong>Age group:</strong> {result.age_group ?? "(missing)"}
            </li>
            <li>
              <strong>Video length (minutes):</strong>{" "}
              {result.video_length_minutes ?? "(missing)"}
            </li>
            <li>
              <strong>Target word count:</strong>{" "}
              {result.target_word_count ?? "(optional)"}
            </li>
            <li>
              <strong>Is complete:</strong> {String(result.is_complete)}
            </li>
            <li>
              <strong>Attempts used:</strong> {result.attempts_used}
            </li>
          </ul>

          {result.follow_up.length > 0 && (
            <>
              <h3>Follow-up needed</h3>
              <ul className="result-list" data-testid="follow-up-list">
                {result.follow_up.map((item) => (
                  <li key={item.field}>
                    <strong>{item.field}:</strong> {item.question}
                  </li>
                ))}
              </ul>
            </>
          )}

          {result.is_complete && (
            <div className="action-row">
              <button
                type="button"
                className="primary-button"
                onClick={() => {
                  void onCreateDraft();
                }}
                disabled={creatingDraft || submitting}
              >
                {creatingDraft ? "Creating draft…" : "Create content draft"}
              </button>
            </div>
          )}
        </section>
      )}
    </>
  );
}
