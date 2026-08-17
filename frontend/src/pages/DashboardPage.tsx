import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getDashboard } from "../lib/coursesApi";
import type { DashboardOut } from "../lib/types";
import { CenteredNote } from "../components/Guards";

const SWATCH_BG = ["var(--color-accent-100)", "var(--color-accent-2-100)"];
const SWATCH_FG = ["var(--color-accent-700)", "var(--color-accent-2-700)"];

function initialsOf(title: string): string {
  const words = title.trim().split(/\s+/).filter(Boolean);
  return ((words[0]?.[0] ?? "?") + (words[1]?.[0] ?? "")).toUpperCase();
}

export function DashboardPage() {
  const navigate = useNavigate();
  const [data, setData] = useState<DashboardOut | null>(null);

  useEffect(() => {
    getDashboard().then(setData);
  }, []);

  if (!data) return <CenteredNote text="Loading…" />;

  const { stats, enrolled_courses } = data;

  return (
    <div>
      <h1 style={{ fontFamily: "var(--font-heading)", fontSize: 32, margin: "0 0 var(--space-5)" }}>My progress</h1>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "var(--space-4)", marginBottom: "var(--space-6)" }}>
        <StatTile value={stats.stat_enrolled} label="Enrolled courses" />
        <StatTile value={stats.stat_completed} label="Completed" />
        <StatTile value={`${stats.stat_avg_score}%`} label="Average quiz score" />
        <StatTile value={stats.stat_certificates} label="Certificates earned" />
      </div>

      {enrolled_courses.length > 0 ? (
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-3)" }}>
          {enrolled_courses.map((ec) => (
            <div key={ec.id} className="card" style={{ padding: "var(--space-4)", display: "flex", alignItems: "center", gap: "var(--space-4)" }}>
              <div style={{ width: 56, height: 56, borderRadius: "var(--radius-lg)", background: SWATCH_BG[ec.swatch % 2], display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                <span style={{ fontFamily: "var(--font-heading)", fontSize: 20, color: SWATCH_FG[ec.swatch % 2] }}>{initialsOf(ec.title)}</span>
              </div>
              <div style={{ flex: 1 }}>
                <p style={{ margin: 0, fontWeight: 600 }}>{ec.title}</p>
                <div style={{ height: 8, borderRadius: 999, background: "var(--color-neutral-200)", overflow: "hidden", margin: "8px 0 4px", maxWidth: 320 }}>
                  <div style={{ height: "100%", width: `${ec.progress_pct}%`, background: "var(--color-accent-2-600)" }} />
                </div>
                <p style={{ fontSize: 12, opacity: 0.6, margin: 0 }}>
                  {ec.done_count} of {ec.lesson_total} lessons{ec.quiz_attempted ? ` · quiz ${ec.quiz_score}%` : ""}
                </p>
              </div>
              {ec.has_certificate && <span className="tag tag-accent-2">Certificate earned</span>}
              <button type="button" className="btn btn-secondary" onClick={() => navigate(`/courses/${ec.id}`)}>
                {ec.progress_pct === 100 ? "Review" : "Continue"}
              </button>
            </div>
          ))}
        </div>
      ) : (
        <div className="card" style={{ padding: "var(--space-6)", textAlign: "center" }}>
          <p style={{ margin: "0 0 var(--space-4)", opacity: 0.7 }}>You haven't enrolled in any courses yet.</p>
          <button type="button" className="btn btn-primary" onClick={() => navigate("/catalog")}>
            Browse the catalog
          </button>
        </div>
      )}
    </div>
  );
}

function StatTile({ value, label }: { value: string | number; label: string }) {
  return (
    <div className="card" style={{ padding: "var(--space-4)" }}>
      <p style={{ fontSize: 28, fontFamily: "var(--font-heading)", margin: 0 }}>{value}</p>
      <p style={{ fontSize: 13, opacity: 0.65, margin: "4px 0 0" }}>{label}</p>
    </div>
  );
}
