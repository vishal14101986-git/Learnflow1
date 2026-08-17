import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { myCourses } from "../lib/instructorApi";
import type { InstructorCourseListItem } from "../lib/types";
import { PlusIcon } from "../components/icons";
import { CenteredNote } from "../components/Guards";

const SWATCH_BG = ["var(--color-accent-100)", "var(--color-accent-2-100)"];
const SWATCH_FG = ["var(--color-accent-700)", "var(--color-accent-2-700)"];

function initialsOf(title: string): string {
  const words = title.trim().split(/\s+/).filter(Boolean);
  return ((words[0]?.[0] ?? "?") + (words[1]?.[0] ?? "")).toUpperCase();
}

export function InstructorCourseListPage() {
  const navigate = useNavigate();
  const [courses, setCourses] = useState<InstructorCourseListItem[] | null>(null);

  useEffect(() => {
    myCourses().then(setCourses);
  }, []);

  if (!courses) return <CenteredNote text="Loading…" />;

  return (
    <div>
      <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", marginBottom: "var(--space-5)" }}>
        <h1 style={{ fontFamily: "var(--font-heading)", fontSize: 32, margin: 0 }}>My courses</h1>
        <button type="button" className="btn btn-primary" onClick={() => navigate("/instructor/courses/new")}>
          <PlusIcon size={15} /> New course
        </button>
      </div>

      {courses.length === 0 ? (
        <div className="card" style={{ padding: "var(--space-6)", textAlign: "center" }}>
          <p style={{ margin: "0 0 var(--space-4)", opacity: 0.7 }}>You haven't created any courses yet.</p>
          <button type="button" className="btn btn-primary" onClick={() => navigate("/instructor/courses/new")}>
            Create your first course
          </button>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-3)" }}>
          {courses.map((c) => (
            <div key={c.id} className="card" style={{ padding: "var(--space-4)", display: "flex", alignItems: "center", gap: "var(--space-4)" }}>
              <div style={{ width: 48, height: 48, borderRadius: "var(--radius-lg)", background: SWATCH_BG[c.swatch % 2], display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                <span style={{ fontFamily: "var(--font-heading)", fontSize: 17, color: SWATCH_FG[c.swatch % 2] }}>{initialsOf(c.title)}</span>
              </div>
              <div style={{ flex: 1 }}>
                <p style={{ margin: 0, fontWeight: 600 }}>{c.title}</p>
                <p style={{ margin: "2px 0 0", fontSize: 12, opacity: 0.6 }}>
                  {c.students} students · {c.completion_rate}% completion · ★ {c.rating ?? "—"}
                </p>
              </div>
              <button type="button" className="btn btn-secondary" onClick={() => navigate(`/instructor/courses/${c.id}/edit`)}>
                Edit
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
