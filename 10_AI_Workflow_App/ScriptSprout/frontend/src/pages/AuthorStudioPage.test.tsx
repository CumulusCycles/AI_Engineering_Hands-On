import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AuthorStudioPage } from "./AuthorStudioPage";

function jsonResponse(body: unknown, init?: ResponseInit): Response {
  return new Response(JSON.stringify(body), {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
}

function deferredResponse() {
  let resolve!: (value: Response) => void;
  const promise = new Promise<Response>((r) => {
    resolve = r;
  });
  return { promise, resolve };
}

const CONTENT_ROW = {
  id: 5,
  author_id: 1,
  status: "draft",
  genre: "fantasy",
  subject: "fox",
  title: null,
  prompt_preview: "A fox prompt",
  has_thumbnail: false,
  has_audio: false,
  guardrails_enabled: true,
  guardrails_max_loops: 3,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

const CONTENT_DETAIL = {
  id: 5,
  author_id: 1,
  source_prompt: "A fox prompt",
  subject: "fox",
  genre: "fantasy",
  age_group: "kids",
  video_length_minutes: 10,
  target_word_count: 700,
  title: null,
  description: null,
  synopsis: "A shy fox sings.",
  story_text: null,
  status: "synopsis_generated",
  guardrails_enabled: true,
  guardrails_max_loops: 3,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
  has_thumbnail: false,
  has_audio: false,
  thumbnail_mime_type: null,
  audio_mime_type: null,
  audio_voice: null,
  audio_generated_at: null,
};

const EXTRACT_COMPLETE = {
  subject: "Shy fox learns to sing",
  genre: "fantasy",
  age_group: "kids",
  video_length_minutes: 10,
  target_word_count: 750,
  missing_fields: [],
  is_complete: true,
  follow_up: [],
  attempts_used: 1,
  openai_response_id: "resp_123",
};

const EXTRACT_INCOMPLETE = {
  subject: "Shy fox learns to sing",
  genre: "fantasy",
  age_group: null,
  video_length_minutes: 10,
  target_word_count: null,
  missing_fields: ["age_group"],
  is_complete: false,
  follow_up: [
    {
      field: "age_group",
      question: "Who is the target audience?",
      input_kind: "single_select",
      guidance: null,
      suggested_options: ["kids", "tween"],
    },
  ],
  attempts_used: 1,
  openai_response_id: "resp_inc",
};

const LIST_RESPONSE = { items: [CONTENT_ROW], total: 1, limit: 50, offset: 0 };
const EMPTY_LIST = { items: [], total: 0, limit: 50, offset: 0 };

function mockFetchForStudio(
  overrides?: Record<string, () => Response | Promise<Response>>,
) {
  return vi
    .spyOn(globalThis, "fetch")
    .mockImplementation(async (input, init) => {
      const url = String(input);
      const method = init?.method ?? "GET";

      for (const [pattern, handler] of Object.entries(overrides ?? {})) {
        if (url.includes(pattern)) return handler();
      }

      if (url.includes("/api/content/?")) return jsonResponse(LIST_RESPONSE);
      if (url.match(/\/api\/content\/\d+$/) && method === "GET")
        return jsonResponse(CONTENT_DETAIL);
      if (
        url.endsWith("/api/nlp/extract-story-parameters") &&
        method === "POST"
      ) {
        return jsonResponse(EXTRACT_COMPLETE);
      }
      if (url.endsWith("/api/content/") && method === "POST") {
        return jsonResponse(CONTENT_DETAIL);
      }
      if (url.match(/\/api\/content\/\d+\//) && method === "POST") {
        return jsonResponse(undefined, { status: 204 });
      }
      return jsonResponse({ detail: "Unexpected" }, { status: 404 });
    });
}

afterEach(() => {
  window.sessionStorage.clear();
  cleanup();
  vi.restoreAllMocks();
});

describe("AuthorStudioPage", () => {
  it("shows empty state when no content rows", async () => {
    mockFetchForStudio({ "/api/content/?": () => jsonResponse(EMPTY_LIST) });

    render(
      <MemoryRouter>
        <AuthorStudioPage />
      </MemoryRouter>,
    );

    expect(await screen.findByTestId("no-drafts")).toBeInTheDocument();
  });

  it("loads content rows and shows detail", async () => {
    mockFetchForStudio();

    render(
      <MemoryRouter>
        <AuthorStudioPage />
      </MemoryRouter>,
    );

    expect(await screen.findByTestId("draft-detail")).toBeInTheDocument();
    expect(screen.getByText(/A shy fox sings/)).toBeInTheDocument();
  });

  it("extracts parameters from a prompt", async () => {
    mockFetchForStudio({ "/api/content/?": () => jsonResponse(EMPTY_LIST) });

    render(
      <MemoryRouter>
        <AuthorStudioPage />
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByLabelText("Prompt"), {
      target: { value: "A 10-minute fantasy story about a fox" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Extract parameters" }));

    expect(await screen.findByTestId("extract-result")).toBeInTheDocument();
    expect(screen.getByText(/Shy fox learns to sing/)).toBeInTheDocument();
  });

  it("shows follow-up questions for incomplete extraction", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input, init) => {
      const url = String(input);
      if (url.includes("/api/content/?")) return jsonResponse(EMPTY_LIST);
      if (
        url.endsWith("/api/nlp/extract-story-parameters") &&
        init?.method === "POST"
      ) {
        return jsonResponse(EXTRACT_INCOMPLETE);
      }
      return jsonResponse({ detail: "Unexpected" }, { status: 404 });
    });

    render(
      <MemoryRouter>
        <AuthorStudioPage />
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByLabelText("Prompt"), {
      target: { value: "A fantasy story about a fox" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Extract parameters" }));

    expect(await screen.findByTestId("follow-up-list")).toBeInTheDocument();
    expect(screen.getByText(/Who is the target audience/)).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Create content draft" }),
    ).toBeNull();
  });

  it("shows API error messages for extraction failures", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input, init) => {
      const url = String(input);
      if (url.includes("/api/content/?")) return jsonResponse(EMPTY_LIST);
      if (
        url.endsWith("/api/nlp/extract-story-parameters") &&
        init?.method === "POST"
      ) {
        return jsonResponse({ detail: "Service unavailable" }, { status: 503 });
      }
      return jsonResponse({ detail: "Unexpected" }, { status: 404 });
    });

    render(
      <MemoryRouter>
        <AuthorStudioPage />
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByLabelText("Prompt"), {
      target: { value: "A prompt" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Extract parameters" }));

    await waitFor(() => {
      expect(
        screen.getByText(
          "Service unavailable. Check backend/OpenAI settings and retry.",
        ),
      ).toBeInTheDocument();
    });
  });

  it("disables extract button while extracting", async () => {
    const pending = deferredResponse();
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes("/api/content/?")) return jsonResponse(EMPTY_LIST);
      return pending.promise;
    });

    render(
      <MemoryRouter>
        <AuthorStudioPage />
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByLabelText("Prompt"), {
      target: { value: "A prompt" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Extract parameters" }));

    expect(
      screen.getByRole("button", { name: "Extracting..." }),
    ).toBeDisabled();

    pending.resolve(jsonResponse(EXTRACT_COMPLETE));

    expect(await screen.findByTestId("extract-result")).toBeInTheDocument();
  });

  it("persists extraction to sessionStorage and restores on remount", async () => {
    mockFetchForStudio({ "/api/content/?": () => jsonResponse(EMPTY_LIST) });

    const { unmount } = render(
      <MemoryRouter>
        <AuthorStudioPage />
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByLabelText("Prompt"), {
      target: { value: "Persisted prompt" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Extract parameters" }));

    expect(await screen.findByTestId("extract-result")).toBeInTheDocument();

    unmount();

    // Remount — should restore from sessionStorage
    mockFetchForStudio({ "/api/content/?": () => jsonResponse(EMPTY_LIST) });

    render(
      <MemoryRouter>
        <AuthorStudioPage />
      </MemoryRouter>,
    );

    expect(screen.getByLabelText("Prompt")).toHaveValue("Persisted prompt");
    expect(screen.getByTestId("extract-result")).toHaveTextContent(
      "Shy fox learns to sing",
    );
  });

  it("survives sessionStorage.setItem failure gracefully", async () => {
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new DOMException("QuotaExceededError", "QuotaExceededError");
    });
    mockFetchForStudio({ "/api/content/?": () => jsonResponse(EMPTY_LIST) });

    render(
      <MemoryRouter>
        <AuthorStudioPage />
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByLabelText("Prompt"), {
      target: { value: "A prompt that fills storage" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Extract parameters" }));

    // Extraction should still succeed in-memory despite storage failure
    expect(await screen.findByTestId("extract-result")).toBeInTheDocument();
    expect(screen.getByText(/Shy fox learns to sing/)).toBeInTheDocument();
    expect(screen.queryByText(/err/i)).toBeNull();
  });

  it("POSTs generate-audio with voice_key when Generate audio is clicked", async () => {
    const requests: { url: string; method: string; body?: string }[] = [];
    const detailReady = {
      ...CONTENT_DETAIL,
      synopsis: "A shy fox sings.",
      title: "The Singing Fox",
      description: "A forest tale.",
      story_text: "Once upon a time there was a fox.",
      status: "thumbnail_generated",
      has_thumbnail: true,
      has_audio: false,
    };
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input, init) => {
      const url = String(input);
      const method = init?.method ?? "GET";
      requests.push({ url, method, body: init?.body as string | undefined });
      if (url.includes("/api/content/?")) return jsonResponse(LIST_RESPONSE);
      if (url.match(/\/api\/content\/5$/) && method === "GET")
        return jsonResponse(detailReady);
      if (url.includes("/generate-audio") && method === "POST")
        return jsonResponse(undefined, { status: 204 });
      if (url.match(/\/api\/content\/\d+\//) && method === "POST")
        return jsonResponse(undefined, { status: 204 });
      return jsonResponse({ detail: "Unexpected" }, { status: 404 });
    });

    render(
      <MemoryRouter>
        <AuthorStudioPage />
      </MemoryRouter>,
    );

    await screen.findByTestId("story-media-detail");
    fireEvent.click(screen.getByRole("button", { name: /Generate audio/i }));

    await waitFor(() => {
      const audio = requests.find(
        (r) => r.url.includes("/generate-audio") && r.method === "POST",
      );
      expect(audio?.body).toContain("female_us");
      expect(audio?.body).toContain("voice_key");
    });
  });
});
