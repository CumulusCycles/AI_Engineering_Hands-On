import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import type {
  ContentItemDetail,
  ContentListItem,
  DraftStep,
} from "../types/content";
import { ApiError } from "../services/authApi";
import {
  approveStep,
  generateDescription,
  generateSynopsis,
  generateTitle,
  getContentItem,
  listMyContent,
  regenerateStep,
} from "../services/contentApi";

/**
 * Execute the function's primary application behavior.
 *
 * @param error Error object captured from a failed async/API operation.
 * @returns Result generated for the caller.
 */
function draftErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 401) {
      return "Your session expired. Please login again.";
    }
    return error.message;
  }
  return "Draft review request failed.";
}

/**
 * Execute the function's primary application behavior.
 */
export function DraftReviewPage() {
  const [searchParams] = useSearchParams();
  const requestedContentId = Number(searchParams.get("contentId"));
  const hasRequestedContentId =
    Number.isFinite(requestedContentId) && requestedContentId > 0;
  // Track local approve state for each step
  // Removed unused 'approved' state
  const [items, setItems] = useState<ContentListItem[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [detail, setDetail] = useState<ContentItemDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionBusy, setActionBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Load content list and preselect the first item when available.
   */
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
          if (
            hasRequestedContentId &&
            page.items.some((item) => item.id === requestedContentId)
          ) {
            setSelectedId(requestedContentId);
          } else {
            setSelectedId(page.items[0].id);
          }
        } else {
          setSelectedId(null);
          setDetail(null);
        }
        // Reset approve state on content change
        setApproved({ synopsis: false, title: false, description: false });
      } catch (error_: unknown) {
        setError(draftErrorMessage(error_));
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, [hasRequestedContentId, requestedContentId]);

  /**
   * Load detail for currently selected row.
   */
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
        // Reset approve state on row change
        setApproved({ synopsis: false, title: false, description: false });
      } catch (error_: unknown) {
        setError(draftErrorMessage(error_));
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
      setError(draftErrorMessage(error_));
    } finally {
      setActionBusy(false);
    }
  }

  /**
   * Execute the function's primary application behavior.
   *
   * @param step Draft step name used for approval or regeneration.
   */
  async function onApprove(step: DraftStep) {
    await runAction(async (contentId) => approveStep(contentId, step));
    setApproved((prev) => ({ ...prev, [step]: true }));
  }

  /**
   * Execute the function's primary application behavior.
   *
   * @param step Draft step name used for approval or regeneration.
   */
  async function onRegenerate(step: DraftStep) {
    await runAction(async (contentId) => regenerateStep(contentId, step));
    setApproved((prev) => ({ ...prev, [step]: false }));
  }

  return (
    <>
      <h2>Draft review</h2>
      <p className="muted">
        Generate, approve, and regenerate synopsis/title/description for your
        content rows.
      </p>

      {loading && <p className="muted">Loading drafts…</p>}
      {error && <p className="err">{error}</p>}

      {!loading && !hasRows && (
        <p className="muted" data-testid="no-drafts">
          No content rows found yet. Create one via API or upcoming workspace
          flow.
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
            <section className="group" data-testid="draft-detail">
              <h3>Current detail</h3>
              <ul className="result-list">
                <li>
                  <strong>Status:</strong> {detail.status}
                </li>
                <li>
                  <strong>Synopsis:</strong> {detail.synopsis ?? "(none)"}
                </li>
                <li>
                  <strong>Title:</strong> {detail.title ?? "(none)"}
                </li>
                <li>
                  <strong>Description:</strong> {detail.description ?? "(none)"}
                </li>
              </ul>

              <div className="action-grid">
                <button
                  type="button"
                  onClick={() => {
                    void runAction(generateSynopsis);
                  }}
                  disabled={actionBusy}
                >
                  Generate synopsis
                </button>
                <button
                  type="button"
                  onClick={() => {
                    void onApprove("synopsis");
                  }}
                  disabled={actionBusy}
                >
                  Approve synopsis
                </button>
                <button
                  type="button"
                  onClick={() => {
                    void onRegenerate("synopsis");
                  }}
                  disabled={actionBusy}
                >
                  Regenerate synopsis
                </button>

                <button
                  type="button"
                  onClick={() => {
                    void runAction(generateTitle);
                  }}
                  disabled={actionBusy}
                >
                  Generate title
                </button>
                <button
                  type="button"
                  onClick={() => {
                    void onApprove("title");
                  }}
                  disabled={actionBusy}
                >
                  Approve title
                </button>
                <button
                  type="button"
                  onClick={() => {
                    void onRegenerate("title");
                  }}
                  disabled={actionBusy}
                >
                  Regenerate title
                </button>

                <button
                  type="button"
                  onClick={() => {
                    void runAction(generateDescription);
                  }}
                  disabled={actionBusy}
                >
                  Generate description
                </button>
                <button
                  type="button"
                  onClick={() => {
                    void onApprove("description");
                  }}
                  disabled={actionBusy}
                >
                  Approve description
                </button>
                <button
                  type="button"
                  onClick={() => {
                    void onRegenerate("description");
                  }}
                  disabled={actionBusy}
                >
                  Regenerate description
                </button>
              </div>
            </section>
          )}
        </>
      )}
    </>
  );
}
