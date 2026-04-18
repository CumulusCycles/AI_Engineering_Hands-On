import { useEffect, useState } from "react";
import { ApiError } from "../services/authApi";
import { getAdminMetrics } from "../services/adminApi";
import type { AdminMetricsResponse, LabelCountBucket } from "../types/admin";

/**
 * Execute the function's primary application behavior.
 *
 * @param error Error object captured from a failed async/API operation.
 * @returns Result generated for the caller.
 */
function metricsErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 401) {
      return "Your session expired. Please login again.";
    }
    if (error.status === 403) {
      return "Only admins can access dashboard metrics.";
    }
    return error.message;
  }
  return "Could not load admin metrics.";
}

/**
 * Execute the function's primary application behavior.
 *
 * @param { title, rows } Input value used to perform this operation.
 */
const BAR_COLORS = [
  "#4CAF50",
  "#2196F3",
  "#F4C542",
  "#FF7043",
  "#AB47BC",
  "#26A69A",
  "#EF5350",
  "#5C6BC0",
];

function BucketChart({
  title,
  rows,
}: {
  title: string;
  rows: LabelCountBucket[];
}) {
  const maxCount = Math.max(...rows.map((r) => r.count), 1);

  return (
    <section className="group">
      <h3>{title}</h3>
      {rows.length === 0 ? (
        <p className="muted">No data in this window.</p>
      ) : (
        <div className="bar-chart" data-testid={`chart-${title}`}>
          {rows.map((row, i) => (
            <div className="bar-row" key={`${title}-${row.label}`}>
              <span className="bar-label">{row.label}</span>
              <div className="bar-track">
                <div
                  className="bar-fill"
                  style={{
                    width: `${(row.count / maxCount) * 100}%`,
                    backgroundColor: BAR_COLORS[i % BAR_COLORS.length],
                  }}
                />
              </div>
              <span className="bar-count">{row.count}</span>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

/**
 * Execute the function's primary application behavior.
 */
export function AdminDashboardPage() {
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<AdminMetricsResponse | null>(null);

  /**
   * Execute the function's primary application behavior.
   */
  async function loadMetrics() {
    setLoading(true);
    setError(null);
    try {
      const payload = await getAdminMetrics({
        start: start.trim() ? start.trim() : null,
        end: end.trim() ? end.trim() : null,
      });
      setMetrics(payload);
    } catch (error_: unknown) {
      setError(metricsErrorMessage(error_));
      setMetrics(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    /**
     * Execute the function's primary application behavior.
     */
    async function loadInitialMetrics() {
      setLoading(true);
      setError(null);
      try {
        const payload = await getAdminMetrics();
        setMetrics(payload);
      } catch (error_: unknown) {
        setError(metricsErrorMessage(error_));
        setMetrics(null);
      } finally {
        setLoading(false);
      }
    }

    void loadInitialMetrics();
  }, []);

  return (
    <>
      <h2>Admin dashboard</h2>
      <p className="muted">
        Read-only usage metrics across content, model calls, generation runs,
        and audit activity.
      </p>

      <form
        className="auth-form"
        onSubmit={(event) => {
          event.preventDefault();
          void loadMetrics();
        }}
      >
        <label>
          Start (ISO 8601)
          <input
            name="start"
            placeholder="2026-03-01T00:00:00Z"
            value={start}
            onChange={(event) => setStart(event.target.value)}
          />
        </label>
        <label>
          End (ISO 8601)
          <input
            name="end"
            placeholder="2026-03-31T23:59:59Z"
            value={end}
            onChange={(event) => setEnd(event.target.value)}
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? "Refreshing…" : "Refresh metrics"}
        </button>
      </form>

      {error && <p className="err">{error}</p>}
      {!error && loading && <p className="muted">Loading metrics…</p>}

      {metrics && (
        <>
          <section className="group" data-testid="metrics-window">
            <h3>Window</h3>
            <p className="muted">
              {metrics.window.start} → {metrics.window.end}
            </p>
          </section>

          <section className="metric-cards" data-testid="metrics-cards">
            <article className="metric-card">
              <h3>Content created</h3>
              <p>{metrics.content.items_created}</p>
            </article>
            <article className="metric-card">
              <h3>Model calls</h3>
              <p>{metrics.model_calls.total}</p>
            </article>
            <article className="metric-card">
              <h3>Generation runs</h3>
              <p>{metrics.generation_runs.total}</p>
            </article>
            <article className="metric-card">
              <h3>Guardrails events</h3>
              <p>{metrics.guardrails.events_total}</p>
            </article>
          </section>

          <BucketChart
            title="Content by status"
            rows={metrics.content.by_status}
          />
          <BucketChart
            title="Content by genre"
            rows={metrics.content.by_genre}
          />
          <BucketChart
            title="Model usage by purpose"
            rows={metrics.model_calls.by_purpose}
          />
          <BucketChart
            title="Model usage by model"
            rows={metrics.model_calls.by_model}
          />
          <BucketChart
            title="Generation runs by status"
            rows={metrics.generation_runs.by_status}
          />
          <BucketChart
            title="Audit events by type"
            rows={metrics.audit.by_event_type}
          />
        </>
      )}
    </>
  );
}
