import { useEffect, useMemo, useState } from "react";
import type { ContentItemDetail, ContentListItem } from "../types/content";
import { ApiError } from "../services/authApi";
import {
  audioUrl,
  generateAudio,
  generateStory,
  generateThumbnail,
  getContentItem,
  listMyContent,
  thumbnailUrl,
} from "../services/contentApi";

/**
 * Execute the function's primary application behavior.
 *
 * @param error Error object captured from a failed async/API operation.
 * @returns Result generated for the caller.
 */
function storyMediaErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 401) {
      return "Your session expired. Please login again.";
    }
    return error.message;
  }
  return "Story/media request failed.";
}

/**
 * Execute the function's primary application behavior.
 */
export function StoryMediaPage() {
  const [items, setItems] = useState<ContentListItem[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [detail, setDetail] = useState<ContentItemDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionBusy, setActionBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    /**
     * Execute the function's primary application behavior.
     */
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const page = await listMyContent();
        setItems(page.items);
        if (page.items.length > 0) {
          setSelectedId(page.items[0].id);
        } else {
          setSelectedId(null);
          setDetail(null);
        }
      } catch (error_: unknown) {
        setError(storyMediaErrorMessage(error_));
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, []);

  useEffect(() => {
    if (selectedId === null) {
      return;
    }
    const contentId = selectedId;
    /**
     * Execute the function's primary application behavior.
     */
    async function loadDetail() {
      try {
        const row = await getContentItem(contentId);
        setDetail(row);
      } catch (error_: unknown) {
        setError(storyMediaErrorMessage(error_));
      }
    }
    void loadDetail();
  }, [selectedId]);

  const hasRows = useMemo(() => items.length > 0, [items]);

  /**
   * Execute the workflow and return its result.
   *
   * @param operation Callback that performs a content action.
   */
  async function runAction(operation: (contentId: number) => Promise<void>) {
    if (selectedId === null) {
      return;
    }
    setActionBusy(true);
    setError(null);
    try {
      await operation(selectedId);
      const refreshed = await getContentItem(selectedId);
      setDetail(refreshed);
    } catch (error_: unknown) {
      setError(storyMediaErrorMessage(error_));
    } finally {
      setActionBusy(false);
    }
  }

  return (
    <>
      <h2>Story + media</h2>
      <p className="muted">
        Generate story text with guardrails, then produce thumbnail and
        narration audio for selected content rows.
      </p>

      {loading && <p className="muted">Loading content…</p>}
      {error && <p className="err">{error}</p>}

      {!loading && !hasRows && (
        <p className="muted" data-testid="no-story-rows">
          No content rows found yet.
        </p>
      )}

      {!loading && hasRows && (
        <>
          <label className="select-row">
            Content row
            <select
              value={selectedId ?? ""}
              onChange={(event) => setSelectedId(Number(event.target.value))}
            >
              {items.map((item) => (
                <option key={item.id} value={item.id}>
                  #{item.id} — {item.status} — {item.prompt_preview}
                </option>
              ))}
            </select>
          </label>

          {detail && (
            <section className="group" data-testid="story-media-detail">
              <h3>Current detail</h3>
              <ul className="result-list">
                <li>
                  <strong>Status:</strong> {detail.status}
                </li>
                <li>
                  <strong>Story:</strong> {detail.story_text ?? "(none)"}
                </li>
                <li>
                  <strong>Has thumbnail:</strong> {String(detail.has_thumbnail)}
                </li>
                <li>
                  <strong>Has audio:</strong> {String(detail.has_audio)}
                </li>
              </ul>

              <div className="action-grid">
                <button
                  type="button"
                  onClick={() => {
                    void runAction(generateStory);
                  }}
                  disabled={actionBusy}
                >
                  Generate story
                </button>
                <button
                  type="button"
                  onClick={() => {
                    void runAction(generateThumbnail);
                  }}
                  disabled={actionBusy || detail.has_thumbnail}
                >
                  Generate thumbnail
                </button>
                <button
                  type="button"
                  onClick={() => {
                    void runAction(generateAudio);
                  }}
                  disabled={actionBusy || detail.has_audio}
                >
                  Generate audio
                </button>
              </div>

              <div className="media-grid">
                <figure className="media-card">
                  <figcaption>Thumbnail</figcaption>
                  {detail.has_thumbnail ? (
                    <img
                      src={thumbnailUrl(detail.id)}
                      alt={`Thumbnail for content ${detail.id}`}
                    />
                  ) : (
                    <p className="muted">No thumbnail yet.</p>
                  )}
                </figure>

                <figure className="media-card">
                  <figcaption>Audio</figcaption>
                  {detail.has_audio ? (
                    <audio controls src={audioUrl(detail.id)}>
                      <track kind="captions" />
                    </audio>
                  ) : (
                    <p className="muted">No audio yet.</p>
                  )}
                </figure>
              </div>
            </section>
          )}
        </>
      )}
    </>
  );
}
