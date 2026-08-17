import { useEffect, useState } from "react";
import { getAnalytics } from "../lib/instructorApi";
import type { AnalyticsOut } from "../lib/types";
import { CenteredNote } from "../components/Guards";

export function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsOut | null>(null);

  useEffect(() => {
    getAnalytics().then(setData);
  }, []);

  if (!data) return <CenteredNote text="Loading…" />;

  const maxRate = Math.max(1, ...data.courses.map((c) => c.completion_rate));

  return (
    <div>
      <h1 style={{ fontFamily: "var(--font-heading)", fontSize: 32, margin: "0 0 var(--space-5)" }}>Analytics</h1>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "var(--space-4)", marginBottom: "var(--space-6)" }}>
        <StatTile value={data.total_students} label="Total students" />
        <StatTile value={`${data.avg_completion_rate}%`} label="Average completion rate" />
        <StatTile value={`${data.avg_quiz_score_all}%`} label="Average quiz score" />
      </div>

      <h2 style={{ fontFamily: "var(--font-heading)", fontSize: 20, margin: "0 0 var(--space-3)" }}>Completion rate by course</h2>
      <div className="card" style={{ padding: "var(--space-5)", marginBottom: "var(--space-6)" }}>
        <div style={{ display: "flex", alignItems: "flex-end", gap: "var(--space-3)", height: 160 }}>
          {data.courses.map((c) => (
            <div key={c.id} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 6, height: "100%", justifyContent: "flex-end" }}>
              <div
                style={{
                  width: "100%",
                  maxWidth: 36,
                  borderRadius: "6px 6px 0 0",
                  background: "var(--color-accent-2-600)",
                  height: `${Math.max(6, Math.round((c.completion_rate / maxRate) * 130))}px`,
                }}
              />
              <span style={{ fontSize: 11, opacity: 0.6, textAlign: "center" }}>{c.title.split(" ").slice(0, 2).join(" ")}</span>
            </div>
          ))}
        </div>
      </div>

      <h2 style={{ fontFamily: "var(--font-heading)", fontSize: 20, margin: "0 0 var(--space-3)" }}>Course details</h2>
      <div style={{ overflowX: "auto" }}>
        <table className="table">
          <thead>
            <tr>
              <th>Course</th>
              <th>Students</th>
              <th>Completion</th>
              <th>Avg. quiz score</th>
              <th>Rating</th>
            </tr>
          </thead>
          <tbody>
            {data.courses.map((row) => (
              <tr key={row.id}>
                <td>{row.title}</td>
                <td>{row.students}</td>
                <td>{row.completion_rate}%</td>
                <td>{row.avg_quiz_score}%</td>
                <td>★ {row.rating ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
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
