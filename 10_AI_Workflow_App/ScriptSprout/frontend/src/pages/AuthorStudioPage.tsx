// Helper: all required params for draft creation must be present
function canCreateDraft(
  result: StoryParametersExtractResponse | null,
): boolean {
  if (!result) return false;
  return (
    !!result.subject &&
    !!result.genre &&
    !!result.age_group &&
    !!result.video_length_minutes &&
    !!result.target_word_count &&
    result.follow_up.length === 0
  );
}
import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import type {
  ContentItemDetail,
  ContentListItem,
  DraftStep,
} from "../types/content";
import type { StoryParametersExtractResponse } from "../types/nlp";
import { ApiError } from "../services/authApi";
import type { TtsVoiceKey } from "../services/contentApi";
import {
  approveStep,
  audioUrl,
  createContentItem,
  generateAudioWithVoice,
  generateDescription,
  generateStory,
  generateSynopsis,
  generateThumbnail,
  generateTitle,
  getContentItem,
  listMyContent,
  regenerateStep,
  thumbnailUrl,
} from "../services/contentApi";
import { extractStoryParameters } from "../services/nlpApi";
/** Logical keys must match backend `GenerateAudioRequest.voice_key`. */
const TTS_VOICE_OPTIONS = [
  { value: "female_us", label: "Female US (nova)" },
  { value: "female_uk", label: "Female UK (fable)" },
  { value: "male_us", label: "Male US (echo)" },
  { value: "male_uk", label: "Male UK (onyx)" },
] as const;
const TTS_VOICE_DEFAULT = "female_us";

/** Matches backend `content.py` `_AUDIO_READY_STATUSES_GR` — audio is allowed after guardrails pass *or* after thumbnail (status moves on). */
const AUDIO_OK_STATUSES_WITH_GUARDRAILS = new Set([
  "guardrails_passed",
  "thumbnail_generated",
  "audio_generated",
]);

function audioBlockedByGuardrails(detail: ContentItemDetail): boolean {
  return (
    detail.guardrails_enabled &&
    !AUDIO_OK_STATUSES_WITH_GUARDRAILS.has(detail.status)
  );
}

const STUDIO_STORAGE_KEY = "scriptsprout.studio.last";

function studioErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 401)
      return "Your session expired. Please login again.";
    if (error.status === 403)
      return "This action is restricted to author accounts.";
    if (error.status === 503)
      return "Service unavailable. Check backend/OpenAI settings and retry.";
    return error.message;
  }
  return "Request failed. Please retry.";
}

export function AuthorStudioPage() {
  const [ttsVoice, setTtsVoice] = useState<TtsVoiceKey>(TTS_VOICE_DEFAULT);
  const [approved, setApproved] = useState<{
    title: boolean;
    description: boolean;
    synopsis: boolean;
  }>({ title: false, description: false, synopsis: false });
  const [accepted, setAccepted] = useState<{
    thumbnail: boolean;
    audio: boolean;
  }>({ thumbnail: false, audio: false });
  const [prompt, setPrompt] = useState(() => {
    const raw = window.sessionStorage.getItem(STUDIO_STORAGE_KEY);
    if (!raw) return "";
    try {
      const parsed = JSON.parse(raw) as { prompt?: string };
      return parsed.prompt ?? "";
    } catch {
      return "";
    }
  });
  const [extractResult, setExtractResult] =
    useState<StoryParametersExtractResponse | null>(() => {
      const raw = window.sessionStorage.getItem(STUDIO_STORAGE_KEY);
      if (!raw) return null;
      try {
        const parsed = JSON.parse(raw) as {
          extractResult?: StoryParametersExtractResponse | null;
        };
        return parsed.extractResult ?? null;
      } catch {
        return null;
      }
    });
  const [items, setItems] = useState<ContentListItem[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [detail, setDetail] = useState<ContentItemDetail | null>(null);
  const [loadingRows, setLoadingRows] = useState(true);
  const [extracting, setExtracting] = useState(false);
  const [creatingDraft, setCreatingDraft] = useState(false);
  // Create content draft from extracted parameters
  async function onCreateDraft() {
    if (!extractResult || !canCreateDraft(extractResult)) return;
    setCreatingDraft(true);
    setError(null);
    try {
      const newItem = await createContentItem({
        prompt,
        subject: extractResult.subject,
        genre: extractResult.genre,
        age_group: extractResult.age_group,
        video_length_minutes: extractResult.video_length_minutes,
        target_word_count: extractResult.target_word_count,
      });
      await refreshRows(newItem.id);
      setSelectedId(newItem.id);
    } catch (error_: unknown) {
      setError(studioErrorMessage(error_));
    } finally {
      setCreatingDraft(false);
    }
  }
  const [actionBusy, setActionBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canExtract = useMemo(
    () => prompt.trim().length > 0 && !extracting,
    [prompt, extracting],
  );
  const hasRows = items.length > 0;

  async function refreshRows(preferredId?: number) {
    setLoadingRows(true);
    try {
      const page = await listMyContent();
      setItems(page.items);
      if (page.items.length === 0) {
        setSelectedId(null);
        setDetail(null);
      } else if (
        preferredId &&
        page.items.some((row) => row.id === preferredId)
      ) {
        setSelectedId(preferredId);
      } else if (
        !selectedId ||
        !page.items.some((row) => row.id === selectedId)
      ) {
        setSelectedId(page.items[0].id);
      }
    } finally {
      setLoadingRows(false);
    }
  }

  useEffect(() => {
    void refreshRows();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (selectedId === null) return;
    const contentId = selectedId;
    async function loadDetail() {
      try {
        const row = await getContentItem(contentId);
        setDetail(row);
        setApproved({
          synopsis: !!row.synopsis,
          title: !!row.title,
          description: !!row.description,
        });
      } catch (error_: unknown) {
        setError(studioErrorMessage(error_));
      }
    }
    void loadDetail();
  }, [selectedId]);

  async function onExtract(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canExtract) return;
    setExtracting(true);
    setError(null);
    try {
      const extracted = await extractStoryParameters({ prompt });
      setExtractResult(extracted);
      try {
        window.sessionStorage.setItem(
          STUDIO_STORAGE_KEY,
          JSON.stringify({ prompt, extractResult: extracted }),
        );
      } catch {
        /* storage full — extraction still usable in-memory */
      }
    } catch (error_: unknown) {
      setError(studioErrorMessage(error_));
      setExtractResult(null);
    } finally {
      setExtracting(false);
    }
  }

  async function runAction(
    operation: (contentId: number) => Promise<void>,
    opts?: { isGeneration?: boolean; resetApprovedStep?: DraftStep },
  ) {
    if (selectedId === null) return;
    setActionBusy(true);
    try {
      await operation(selectedId);
      await refreshRows(selectedId);
      // After rows are refreshed, get the latest detail
      const refreshed = await getContentItem(selectedId);
      setDetail(structuredClone(refreshed));
      // Always reset approval for the step if generation/regeneration
      if (opts?.resetApprovedStep) {
        setApproved((prev) => ({ ...prev, [opts.resetApprovedStep!]: false }));
      }
      setError(null); // Clear error only on success
    } catch (error_: unknown) {
      // Always try to show the most specific error message
      let message: string | null = null;
      // Robustly detect 401 status
      let status: number | undefined;
      if (typeof error_ === "object" && error_ !== null) {
        if (
          "status" in error_ &&
          typeof (error_ as { status?: unknown }).status === "number"
        ) {
          status = (error_ as { status: number }).status;
        } else if (
          "statusCode" in error_ &&
          typeof (error_ as { statusCode?: unknown }).statusCode === "number"
        ) {
          status = (error_ as { statusCode: number }).statusCode;
        }
      }
      if (status === 401) {
        message = "Your session expired. Please login again.";
      } else if (error_ instanceof ApiError) {
        message = studioErrorMessage(error_);
      } else if (
        error_ &&
        typeof error_ === "object" &&
        "message" in error_ &&
        typeof (error_ as { message?: unknown }).message === "string"
      ) {
        message = String((error_ as { message: unknown }).message);
      } else if (
        error_ &&
        typeof error_ === "object" &&
        "detail" in error_ &&
        typeof (error_ as { detail?: unknown }).detail === "string"
      ) {
        message = String((error_ as { detail: unknown }).detail);
      }
      if (!message && opts?.isGeneration) {
        message = "Generation failed";
      } else if (!message) {
        message = studioErrorMessage(error_);
      }
      setError(message);
    } finally {
      setActionBusy(false);
    }
  }

  async function onApprove(step: DraftStep) {
    setError(null);
    await runAction(async (contentId) => approveStep(contentId, step));
    setApproved((prev) => ({ ...prev, [step]: true }));
  }

  async function onRegenerate(step: DraftStep) {
    setError(null);
    await runAction(async (contentId) => regenerateStep(contentId, step), {
      resetApprovedStep: step,
    });
  }

  const handleGenerateSynopsis = () => {
    runAction(
      async (id) => {
        await generateSynopsis(id);
        // After generation, force approval reset for synopsis
        setApproved((prev) => ({ ...prev, synopsis: false }));
      },
      { isGeneration: true, resetApprovedStep: "synopsis" },
    );
  };
  const handleGenerateTitle = () => {
    runAction(
      async (id) => {
        await generateTitle(id);
        setApproved((prev) => ({ ...prev, title: false }));
      },
      { isGeneration: true, resetApprovedStep: "title" },
    );
  };
  const handleGenerateDescription = () => {
    runAction(
      async (id) => {
        await generateDescription(id);
        setApproved((prev) => ({ ...prev, description: false }));
      },
      { isGeneration: true, resetApprovedStep: "description" },
    );
  };
  const handleGenerateStory = () => {
    runAction(generateStory, { isGeneration: true });
  };
  const handleGenerateThumbnail = () => {
    runAction(
      async (id) => {
        try {
          await generateThumbnail(id);
        } catch (err: unknown) {
          if (
            err instanceof Error &&
            err.message &&
            err.message.includes("guardrails")
          ) {
            setError("You must pass guardrails before generating a thumbnail.");
            return;
          }
          throw err;
        }
      },
      { isGeneration: true },
    );
  };
  const handleGenerateAudio = () => {
    runAction(
      async (id) => {
        try {
          await generateAudioWithVoice(id, ttsVoice);
        } catch (err: unknown) {
          if (
            err instanceof Error &&
            err.message &&
            err.message.includes("guardrails")
          ) {
            setError("You must pass guardrails before generating audio.");
            return;
          }
          throw err;
        }
      },
      { isGeneration: true },
    );
  };

  return (
    <>
      <h2>Author studio</h2>
      <p className="muted">
        Complete the full author flow in one place: extract, draft, review,
        generate story, and create media.
      </p>
      {error && (
        <div className="err" data-testid="studio-error">
          {error}
        </div>
      )}

      <section className="group studio-section">
        <h3>1) Prompt extraction</h3>
        <form className="auth-form" onSubmit={(event) => void onExtract(event)}>
          <label>
            Prompt
            <textarea
              name="prompt"
              rows={5}
              placeholder="Create a 10-minute fantasy story for kids..."
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
            />
          </label>
          <button type="submit" disabled={!canExtract}>
            {extracting ? "Extracting..." : "Extract parameters"}
          </button>
        </form>

        {extractResult && (
          <div data-testid="extract-result">
            <ul className="result-list">
              <li>
                <strong>Subject:</strong> {extractResult.subject ?? "(missing)"}
              </li>
              <li>
                <strong>Genre:</strong> {extractResult.genre ?? "(missing)"}
              </li>
              <li>
                <strong>Age group:</strong>{" "}
                {extractResult.age_group ?? "(missing)"}
              </li>
              <li>
                <strong>Length (minutes):</strong>{" "}
                {extractResult.video_length_minutes ?? "(missing)"}
              </li>
              <li>
                <strong>Target words:</strong>{" "}
                {extractResult.target_word_count ?? "(optional)"}
              </li>
            </ul>
            {extractResult.follow_up.length > 0 && (
              <ul className="result-list" data-testid="follow-up-list">
                {extractResult.follow_up.map((item) => (
                  <li key={item.field}>
                    <strong>{item.field}:</strong> {item.question}
                  </li>
                ))}
              </ul>
            )}
            {extractResult.is_complete && (
              <div className="action-row">
                <button
                  type="button"
                  className="primary-button"
                  onClick={() => void onCreateDraft()}
                  disabled={creatingDraft || !canCreateDraft(extractResult)}
                >
                  {creatingDraft ? "Creating draft..." : "Create content draft"}
                </button>
              </div>
            )}
          </div>
        )}
      </section>

      <section className="group studio-section">
        <h3>2) Select content row</h3>
        {loadingRows && <p className="muted">Loading content...</p>}
        {!loadingRows && !hasRows && (
          <p className="muted" data-testid="no-drafts">
            No content rows found yet. Create one from extraction above.
          </p>
        )}
        {!loadingRows && hasRows && (
          <label className="select-row">
            Content row
            <select
              value={selectedId ?? ""}
              onChange={(event) => setSelectedId(Number(event.target.value))}
            >
              {items.map((item) => (
                <option key={item.id} value={item.id}>
                  #{item.id} - {item.status} - {item.prompt_preview}
                </option>
              ))}
            </select>
          </label>
        )}
      </section>

      {detail && (
        <>
          <section className="group studio-section" data-testid="draft-detail">
            <h3>3) Draft review actions</h3>
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
              {/* SYNOPSIS BUTTONS */}
              <button
                type="button"
                className="action-generate"
                disabled={actionBusy || !!detail.synopsis || approved.synopsis}
                onClick={handleGenerateSynopsis}
                aria-busy={actionBusy ? "true" : undefined}
              >
                Generate synopsis
              </button>
              <button
                type="button"
                className="action-approve-green"
                disabled={actionBusy || !detail.synopsis || approved.synopsis}
                aria-busy={actionBusy ? "true" : undefined}
                onClick={() => void onApprove("synopsis")}
              >
                Approve synopsis
              </button>
              <button
                type="button"
                className="action-regenerate"
                disabled={actionBusy || !detail.synopsis || approved.synopsis}
                aria-busy={actionBusy ? "true" : undefined}
                onClick={() => void onRegenerate("synopsis")}
              >
                Regenerate synopsis
              </button>
              {/* TITLE BUTTONS */}
              <button
                type="button"
                className="action-generate"
                disabled={
                  actionBusy ||
                  !approved.synopsis ||
                  !!detail.title ||
                  approved.title
                }
                onClick={handleGenerateTitle}
                aria-busy={actionBusy ? "true" : undefined}
              >
                Generate title
              </button>
              <button
                type="button"
                className="action-approve-green"
                disabled={actionBusy || !detail.title || approved.title}
                aria-busy={actionBusy ? "true" : undefined}
                onClick={() => void onApprove("title")}
              >
                Approve title
              </button>
              <button
                type="button"
                className="action-regenerate"
                disabled={actionBusy || !detail.title || approved.title}
                aria-busy={actionBusy ? "true" : undefined}
                onClick={() => void onRegenerate("title")}
              >
                Regenerate title
              </button>
              {/* DESCRIPTION BUTTONS */}
              <button
                type="button"
                className="action-generate"
                disabled={
                  actionBusy ||
                  !approved.title ||
                  !!detail.description ||
                  approved.description
                }
                onClick={handleGenerateDescription}
                aria-busy={actionBusy ? "true" : undefined}
              >
                Generate description
              </button>
              <button
                type="button"
                className="action-approve-green"
                disabled={
                  actionBusy || !detail.description || approved.description
                }
                aria-busy={actionBusy ? "true" : undefined}
                onClick={() => void onApprove("description")}
              >
                Approve description
              </button>
              <button
                type="button"
                className="action-regenerate"
                disabled={
                  actionBusy || !detail.description || approved.description
                }
                aria-busy={actionBusy ? "true" : undefined}
                onClick={() => void onRegenerate("description")}
              >
                Regenerate description
              </button>
            </div>
          </section>

          <section
            className="group studio-section"
            data-testid="story-media-detail"
          >
            <h3>4) Story + media generation</h3>
            <ul className="result-list">
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
                className="action-approve-green"
                disabled={
                  actionBusy ||
                  !approved.title ||
                  !approved.description ||
                  !!detail.story_text
                }
                onClick={handleGenerateStory}
                aria-busy={actionBusy ? "true" : undefined}
              >
                {actionBusy ? (
                  <>
                    <span
                      className="spinner"
                      aria-hidden="true"
                      style={{ marginRight: 8 }}
                    />
                    Generating…
                  </>
                ) : (
                  "Generate story"
                )}
              </button>
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "flex-start",
                  gap: 4,
                  minWidth: 200,
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                    width: "100%",
                  }}
                >
                  <button
                    type="button"
                    className="action-approve-green"
                    disabled={
                      actionBusy ||
                      accepted.thumbnail ||
                      !detail.story_text ||
                      (detail.guardrails_enabled &&
                        detail.status !== "guardrails_passed")
                    }
                    onClick={handleGenerateThumbnail}
                    aria-busy={actionBusy ? "true" : undefined}
                    style={{ flex: 1 }}
                    title={
                      detail.guardrails_enabled &&
                      detail.status !== "guardrails_passed"
                        ? "You must pass guardrails before generating a thumbnail."
                        : undefined
                    }
                  >
                    {actionBusy ? (
                      <>
                        <span
                          className="spinner"
                          aria-hidden="true"
                          style={{ marginRight: 8 }}
                        />
                        Generating…
                      </>
                    ) : (
                      "Generate thumbnail"
                    )}
                  </button>
                  <label
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 4,
                      fontSize: 14,
                      marginBottom: 0,
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={accepted.thumbnail}
                      onChange={(e) =>
                        setAccepted((a) => ({
                          ...a,
                          thumbnail: e.target.checked,
                        }))
                      }
                      disabled={actionBusy || !detail.has_thumbnail}
                      style={{ margin: 0 }}
                    />
                    Accept
                  </label>
                </div>
              </div>
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "flex-start",
                  gap: 4,
                  minWidth: 200,
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                    width: "100%",
                  }}
                >
                  <button
                    type="button"
                    className="action-approve-green"
                    disabled={
                      actionBusy ||
                      accepted.audio ||
                      !detail.story_text ||
                      audioBlockedByGuardrails(detail)
                    }
                    onClick={handleGenerateAudio}
                    aria-busy={actionBusy ? "true" : undefined}
                    style={{
                      flex: 1,
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      gap: 6,
                      minWidth: 160,
                      padding: 8,
                    }}
                    title={
                      audioBlockedByGuardrails(detail)
                        ? "Pass story guardrails before narration (or continue after thumbnail if guardrails already passed)."
                        : undefined
                    }
                  >
                    <span>
                      {actionBusy ? (
                        <>
                          <span
                            className="spinner"
                            aria-hidden="true"
                            style={{ marginRight: 8 }}
                          />
                          Generating…
                        </>
                      ) : (
                        "Generate audio"
                      )}
                    </span>
                    <select
                      className="tts-voice-select"
                      value={ttsVoice}
                      onClick={(e) => e.stopPropagation()}
                      onChange={(e) =>
                        setTtsVoice(e.target.value as TtsVoiceKey)
                      }
                      disabled={actionBusy || !detail.story_text}
                      aria-label="Select TTS voice"
                      style={{ marginTop: 6, width: "90%" }}
                    >
                      {TTS_VOICE_OPTIONS.map((opt) => (
                        <option key={opt.value} value={opt.value}>
                          {opt.label}
                        </option>
                      ))}
                    </select>
                  </button>
                  <label
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 4,
                      fontSize: 14,
                      marginBottom: 0,
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={accepted.audio}
                      onChange={(e) =>
                        setAccepted((a) => ({ ...a, audio: e.target.checked }))
                      }
                      disabled={actionBusy || !detail.has_audio}
                      style={{ margin: 0 }}
                    />
                    Accept
                  </label>
                </div>
              </div>
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
        </>
      )}
    </>
  );
}
