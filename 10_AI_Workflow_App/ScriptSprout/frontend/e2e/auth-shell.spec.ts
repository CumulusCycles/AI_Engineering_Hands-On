import { expect, test } from "@playwright/test";
import type { Page } from "@playwright/test";

/**
 * Stub API routes used by the auth shell.
 *
 * Args:
 *   page: Playwright page under test.
 */
async function stubAuthRoutes(page: Page) {
  await page.route("**/health", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ status: "ok", service: "scriptsprout-api" }),
    });
  });

  await page.route("**/api/auth/me", async (route) => {
    await route.fulfill({
      status: 401,
      contentType: "application/json",
      body: JSON.stringify({ detail: "Not authenticated" }),
    });
  });

  await page.route("**/api/auth/login", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        id: 1,
        username: "author_1",
        email: "author_1@example.com",
        email_verified: true,
        role: "author",
        is_active: true,
      }),
    });
  });

  await page.route("**/api/nlp/extract-story-parameters", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        subject: "A shy fox learning to sing",
        genre: "fantasy",
        age_group: null,
        video_length_minutes: 12,
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
        openai_response_id: "resp_123",
      }),
    });
  });

  await page.route("**/api/content/?**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        items: [],
        total: 0,
        limit: 50,
        offset: 0,
      }),
    });
  });
}

test("registers author then completes email verification flow", async ({
  page,
}) => {
  await page.route("**/health", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ status: "ok", service: "scriptsprout-api" }),
    });
  });
  await page.route("**/api/auth/me", async (route) => {
    await route.fulfill({
      status: 401,
      contentType: "application/json",
      body: JSON.stringify({ detail: "Not authenticated" }),
    });
  });
  await page.route("**/api/auth/register", async (route) => {
    await route.fulfill({
      status: 201,
      contentType: "application/json",
      body: JSON.stringify({
        username: "new_author",
        role: "author",
        verification_required: true,
      }),
    });
  });
  await page.route("**/api/auth/email-verification/request", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        message: "Verification token generated and email delivery queued.",
        delivery_channel: "email",
      }),
    });
  });
  await page.route("**/api/auth/email-verification/confirm", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ message: "Email verified successfully." }),
    });
  });

  await page.goto("/");
  await page
    .getByLabel("Primary")
    .getByRole("link", { name: "Register" })
    .click();
  await page.getByLabel("Username").fill("new_author");
  await page
    .getByRole("textbox", { name: "Password", exact: true })
    .fill("password123");
  await page.getByLabel("Confirm password").fill("password123");
  await page.getByRole("button", { name: "Create account" }).click();

  await expect(page).toHaveURL(/\/verify-email\?username=new_author$/);
  await page.getByLabel("Email").fill("new_author@example.com");
  await page.getByRole("button", { name: "Send verification token" }).click();
  await expect(page.getByText("Verification token generated")).toBeVisible();

  await page.getByLabel("Verification token").fill("test-token");
  await page.getByRole("button", { name: "Verify email" }).click();
  await expect(page.getByTestId("verification-success")).toContainText(
    "Verified successfully.",
  );
});

test("shows anonymous home state then login flow", async ({ page }) => {
  await stubAuthRoutes(page);
  await page.goto("/");

  await expect(page.getByTestId("auth-state-anonymous")).toBeVisible();

  await page.getByLabel("Primary").getByRole("link", { name: "Login" }).click();
  await expect(page.getByRole("heading", { name: "Login" })).toBeVisible();

  await page.getByLabel("Username").fill("author_1");
  await page.getByLabel("Password").fill("password123");
  await page.getByRole("button", { name: "Sign in" }).click();

  await expect(page.getByTestId("auth-state-authenticated")).toContainText(
    "author_1",
  );
  await expect(page.getByRole("button", { name: "Logout" })).toBeVisible();
});

test("extracts workspace parameters and renders follow-up guidance", async ({
  page,
}) => {
  await stubAuthRoutes(page);
  await page.goto("/");

  await page.getByLabel("Primary").getByRole("link", { name: "Login" }).click();
  await page.getByLabel("Username").fill("author_1");
  await page.getByLabel("Password").fill("password123");
  await page.getByRole("button", { name: "Sign in" }).click();

  await page
    .getByLabel("Primary")
    .getByRole("link", { name: "Author studio" })
    .click();
  await expect(
    page.getByRole("heading", { name: "Author studio" }),
  ).toBeVisible();

  await page
    .getByLabel("Prompt")
    .fill("A 12-minute fantasy story about a shy fox.");
  await page.getByRole("button", { name: "Extract parameters" }).click();

  await expect(page.getByTestId("extract-result")).toContainText(
    "A shy fox learning to sing",
  );
  await expect(page.getByTestId("follow-up-list")).toContainText(
    "Who is the target audience?",
  );
});

test("creates a draft from workspace extraction and opens draft review", async ({
  page,
}) => {
  await page.route("**/health", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ status: "ok", service: "scriptsprout-api" }),
    });
  });
  await page.route("**/api/auth/me", async (route) => {
    await route.fulfill({
      status: 401,
      contentType: "application/json",
      body: JSON.stringify({ detail: "Not authenticated" }),
    });
  });
  await page.route("**/api/auth/login", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        id: 1,
        username: "author_1",
        role: "author",
        is_active: true,
      }),
    });
  });
  await page.route("**/api/nlp/extract-story-parameters", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        subject: "Shy fox learns to sing",
        genre: "fantasy",
        age_group: "kids",
        video_length_minutes: 10,
        target_word_count: 750,
        missing_fields: [],
        is_complete: true,
        follow_up: [],
        attempts_used: 1,
        openai_response_id: "resp_456",
      }),
    });
  });
  await page.route("**/api/content/", async (route) => {
    await route.fulfill({
      status: 201,
      contentType: "application/json",
      body: JSON.stringify({
        id: 42,
        author_id: 1,
        source_prompt: "A complete prompt",
        subject: "Shy fox learns to sing",
        genre: "fantasy",
        age_group: "kids",
        video_length_minutes: 10,
        target_word_count: 750,
        title: null,
        description: null,
        synopsis: null,
        story_text: null,
        status: "draft",
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
      }),
    });
  });
  await page.route("**/api/content/?**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        items: [
          {
            id: 42,
            author_id: 1,
            status: "draft",
            genre: "fantasy",
            subject: "Shy fox learns to sing",
            title: null,
            prompt_preview: "A complete prompt",
            has_thumbnail: false,
            has_audio: false,
            guardrails_enabled: true,
            guardrails_max_loops: 3,
            created_at: "2026-01-01T00:00:00Z",
            updated_at: "2026-01-01T00:00:00Z",
          },
        ],
        total: 1,
        limit: 50,
        offset: 0,
      }),
    });
  });
  await page.route("**/api/content/42", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        id: 42,
        author_id: 1,
        source_prompt: "A complete prompt",
        subject: "Shy fox learns to sing",
        genre: "fantasy",
        age_group: "kids",
        video_length_minutes: 10,
        target_word_count: 750,
        title: null,
        description: null,
        synopsis: null,
        story_text: null,
        status: "draft",
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
      }),
    });
  });

  await page.goto("/");
  await page.getByLabel("Primary").getByRole("link", { name: "Login" }).click();
  await page.getByLabel("Username").fill("author_1");
  await page.getByLabel("Password").fill("password123");
  await page.getByRole("button", { name: "Sign in" }).click();

  await page
    .getByLabel("Primary")
    .getByRole("link", { name: "Author studio" })
    .click();
  await page.getByRole("textbox", { name: "Prompt" }).fill("A complete prompt");
  await page.getByRole("button", { name: "Extract parameters" }).click();
  await page.getByRole("button", { name: "Create content draft" }).click();

  await expect(page).toHaveURL(/\/studio$/);
  await expect(page.getByTestId("draft-detail")).toBeVisible();
});

test("opens draft review and loads existing row detail", async ({ page }) => {
  await stubAuthRoutes(page);
  await page.route("**/api/content/?**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        items: [
          {
            id: 11,
            author_id: 1,
            status: "synopsis_generated",
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
          },
        ],
        total: 1,
        limit: 50,
        offset: 0,
      }),
    });
  });
  await page.route("**/api/content/11", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        id: 11,
        author_id: 1,
        source_prompt: "A fox prompt",
        subject: "fox",
        genre: "fantasy",
        age_group: null,
        video_length_minutes: 10,
        target_word_count: null,
        title: null,
        description: null,
        synopsis: "A shy fox learns to sing.",
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
      }),
    });
  });

  await page.goto("/");
  await page.getByLabel("Primary").getByRole("link", { name: "Login" }).click();
  await page.getByLabel("Username").fill("author_1");
  await page.getByLabel("Password").fill("password123");
  await page.getByRole("button", { name: "Sign in" }).click();

  await page
    .getByLabel("Primary")
    .getByRole("link", { name: "Author studio" })
    .click();
  await expect(
    page.getByRole("heading", { name: "Author studio" }),
  ).toBeVisible();
  await expect(page.getByTestId("draft-detail")).toContainText(
    "A shy fox learns to sing.",
  );
});

test("opens story/media page and renders generated assets state", async ({
  page,
}) => {
  await stubAuthRoutes(page);
  await page.route("**/api/content/?**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        items: [
          {
            id: 31,
            author_id: 1,
            status: "guardrails_passed",
            genre: "fantasy",
            subject: "fox",
            title: "Fox story",
            prompt_preview: "A fox prompt",
            has_thumbnail: true,
            has_audio: true,
            guardrails_enabled: true,
            guardrails_max_loops: 3,
            created_at: "2026-01-01T00:00:00Z",
            updated_at: "2026-01-01T00:00:00Z",
          },
        ],
        total: 1,
        limit: 50,
        offset: 0,
      }),
    });
  });
  await page.route("**/api/content/31", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        id: 31,
        author_id: 1,
        source_prompt: "A fox prompt",
        subject: "fox",
        genre: "fantasy",
        age_group: "kids",
        video_length_minutes: 10,
        target_word_count: null,
        title: "Fox story",
        description: "Description",
        synopsis: "Synopsis",
        story_text: "Story text",
        status: "guardrails_passed",
        guardrails_enabled: true,
        guardrails_max_loops: 3,
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-01T00:00:00Z",
        has_thumbnail: true,
        has_audio: true,
        thumbnail_mime_type: "image/png",
        audio_mime_type: "audio/mpeg",
        audio_voice: "alloy",
        audio_generated_at: "2026-01-01T00:00:00Z",
      }),
    });
  });
  await page.route("**/api/content/31/thumbnail", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "image/png",
      body: "not-a-real-image",
    });
  });
  await page.route("**/api/content/31/audio", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "audio/mpeg",
      body: "not-real-audio",
    });
  });

  await page.goto("/");
  await page.getByLabel("Primary").getByRole("link", { name: "Login" }).click();
  await page.getByLabel("Username").fill("author_1");
  await page.getByLabel("Password").fill("password123");
  await page.getByRole("button", { name: "Sign in" }).click();

  await page
    .getByLabel("Primary")
    .getByRole("link", { name: "Author studio" })
    .click();
  await expect(
    page.getByRole("heading", { name: "Author studio" }),
  ).toBeVisible();
  await expect(page.getByTestId("story-media-detail")).toContainText(
    "Story text",
  );
});

test("admin can open dashboard and see metrics panels", async ({ page }) => {
  await page.route("**/health", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ status: "ok", service: "scriptsprout-api" }),
    });
  });
  await page.route("**/api/auth/me", async (route) => {
    await route.fulfill({
      status: 401,
      contentType: "application/json",
      body: JSON.stringify({ detail: "Not authenticated" }),
    });
  });
  await page.route("**/api/auth/login", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        id: 2,
        username: "admin_1",
        role: "admin",
        is_active: true,
      }),
    });
  });
  await page.route("**/api/admin/metrics**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        window: {
          start: "2026-03-01T00:00:00Z",
          end: "2026-03-26T00:00:00Z",
          used_default_window: true,
        },
        content: {
          items_created: 12,
          by_status: [{ label: "draft", count: 4 }],
          by_genre: [{ label: "fantasy", count: 6 }],
        },
        model_calls: {
          total: 18,
          success_count: 17,
          failure_count: 1,
          avg_latency_ms: 802.4,
          total_token_input: 1200,
          total_token_output: 4400,
          by_purpose: [{ label: "extract_story_parameters", count: 5 }],
          by_model: [{ label: "gpt-4.1-mini", count: 10 }],
        },
        generation_runs: {
          total: 6,
          by_status: [{ label: "guardrails_passed", count: 5 }],
          avg_story_attempts: 1.2,
          avg_guardrails_attempts: 1.1,
        },
        guardrails: {
          events_total: 7,
          passed_count: 6,
          failed_count: 1,
        },
        audit: {
          events_total: 9,
          by_event_type: [{ label: "approve_synopsis", count: 3 }],
        },
      }),
    });
  });

  await page.goto("/");
  await page.getByLabel("Primary").getByRole("link", { name: "Login" }).click();
  await page.getByLabel("Username").fill("admin_1");
  await page.getByLabel("Password").fill("password123");
  await page.getByRole("button", { name: "Sign in" }).click();

  await page
    .getByLabel("Primary")
    .getByRole("link", { name: "Admin dashboard" })
    .click();
  await expect(
    page.getByRole("heading", { name: "Admin dashboard" }),
  ).toBeVisible();
  await expect(page.getByTestId("metrics-cards")).toContainText("12");
});

test("admin can run NLP query and view composed response", async ({ page }) => {
  await page.route("**/health", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ status: "ok", service: "scriptsprout-api" }),
    });
  });
  await page.route("**/api/auth/me", async (route) => {
    await route.fulfill({
      status: 401,
      contentType: "application/json",
      body: JSON.stringify({ detail: "Not authenticated" }),
    });
  });
  await page.route("**/api/auth/login", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        id: 2,
        username: "admin_1",
        role: "admin",
        is_active: true,
      }),
    });
  });
  await page.route("**/api/admin/nlp-query", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        query: "How many stories this week by genre?",
        plan_summary: "Run metrics and semantic search.",
        parse_attempts_used: 1,
        metrics: {
          window: {
            start: "2026-03-01T00:00:00Z",
            end: "2026-03-26T00:00:00Z",
            used_default_window: false,
          },
          content: {
            items_created: 9,
            by_status: [{ label: "draft", count: 4 }],
            by_genre: [{ label: "fantasy", count: 6 }],
          },
          model_calls: {
            total: 14,
            success_count: 13,
            failure_count: 1,
            avg_latency_ms: 700.0,
            total_token_input: 1000,
            total_token_output: 4000,
            by_purpose: [],
            by_model: [],
          },
          generation_runs: {
            total: 4,
            by_status: [],
            avg_story_attempts: 1.0,
            avg_guardrails_attempts: 1.0,
          },
          guardrails: { events_total: 4, passed_count: 4, failed_count: 0 },
          audit: { events_total: 6, by_event_type: [] },
        },
        semantic_search: {
          embedding_model: "text-embedding-3-small",
          attempts_used: 1,
          items: [
            {
              distance: 0.12,
              content: {
                id: 77,
                author_id: 1,
                status: "draft",
                genre: "fantasy",
                subject: "fox",
                title: "Fox Story",
                prompt_preview: "A fox prompt",
                has_thumbnail: false,
                has_audio: false,
                guardrails_enabled: true,
                guardrails_max_loops: 3,
                created_at: "2026-01-01T00:00:00Z",
                updated_at: "2026-01-01T00:00:00Z",
              },
            },
          ],
        },
      }),
    });
  });

  await page.goto("/");
  await page.getByLabel("Primary").getByRole("link", { name: "Login" }).click();
  await page.getByLabel("Username").fill("admin_1");
  await page.getByLabel("Password").fill("password123");
  await page.getByRole("button", { name: "Sign in" }).click();

  await page
    .getByLabel("Primary")
    .getByRole("link", { name: "Admin NLP query" })
    .click();
  await expect(
    page.getByRole("heading", { name: "Admin NLP query" }),
  ).toBeVisible();
  await page.getByLabel("Query").fill("How many stories this week by genre?");
  await page.getByRole("button", { name: "Run query" }).click();

  await expect(page.getByTestId("admin-nlp-result")).toContainText(
    "Run metrics and semantic search.",
  );
  await expect(page.getByTestId("semantic-hit-list")).toContainText(
    "Fox Story",
  );
});

test("admin NLP query shows API failure message", async ({ page }) => {
  await page.route("**/health", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ status: "ok", service: "scriptsprout-api" }),
    });
  });
  await page.route("**/api/auth/me", async (route) => {
    await route.fulfill({
      status: 401,
      contentType: "application/json",
      body: JSON.stringify({ detail: "Not authenticated" }),
    });
  });
  await page.route("**/api/auth/login", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        id: 2,
        username: "admin_1",
        role: "admin",
        is_active: true,
      }),
    });
  });
  await page.route("**/api/admin/nlp-query", async (route) => {
    await route.fulfill({
      status: 503,
      contentType: "application/json",
      body: JSON.stringify({ detail: "NLP query unavailable" }),
    });
  });

  await page.goto("/");
  await page.getByLabel("Primary").getByRole("link", { name: "Login" }).click();
  await page.getByLabel("Username").fill("admin_1");
  await page.getByLabel("Password").fill("password123");
  await page.getByRole("button", { name: "Sign in" }).click();
  await page
    .getByLabel("Primary")
    .getByRole("link", { name: "Admin NLP query" })
    .click();

  await page.getByLabel("Query").fill("How many stories this week by genre?");
  await page.getByRole("button", { name: "Run query" }).click();

  await expect(page.getByText("NLP query unavailable")).toBeVisible();
});
