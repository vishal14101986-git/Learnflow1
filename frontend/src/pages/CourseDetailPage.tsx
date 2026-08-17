import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { enroll, getCourse } from "../lib/coursesApi";
import type { CourseDetail } from "../lib/types";
import { CheckCircleIcon, CircleIcon, HelpCircleIcon } from "../components/icons";
import { CenteredNote } from "../components/Guards";

const SWATCH_BG = ["var(--color-accent-100)", "var(--color-accent-2-100)"];
const SWATCH_FG = ["var(--color-accent-700)", "var(--color-accent-2-700)"];

function initialsOf(title: string): string {
  const words = title.trim().split(/\s+/).filter(Boolean);
  return ((words[0]?.[0] ?? "?") + (words[1]?.[0] ?? "")).toUpperCase();
}

export function CourseDetailPage() {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [enrolling, setEnrolling] = useState(false);

  const load = useCallback(() => {
    if (!courseId) return;
    getCourse(courseId).then(setCourse);
  }, [courseId]);

  useEffect(() => {
    load();
  }, [load]);

  if (!course) return <CenteredNote text="Loading…" />;

  const bg = SWATCH_BG[course.swatch % 2];
  const fg = SWATCH_FG[course.swatch % 2];

  async function onEnroll() {
    setEnrolling(true);
    try {
      await enroll(course!.id);
      load();
    } finally {
      setEnrolling(false);
    }
  }

  const firstIncomplete = course.lessons.find((l) => !l.done) ?? course.lessons[0];

  return (
    <div>
      <button type="button" className="btn btn-ghost" style={{ marginBottom: "var(--space-4)" }} onClick={() => navigate("/catalog")}>
        &larr; Back to catalog
      </button>

      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "var(--space-6)", alignItems: "start" }}>
        <div>
          <div style={{ height: 180, borderRadius: "var(--radius-lg)", background: bg, display: "flex", alignItems: "center", justifyContent: "center", marginBottom: "var(--space-5)" }}>
            <span style={{ fontFamily: "var(--font-heading)", fontSize: 56, color: fg }}>{initialsOf(course.title)}</span>
          </div>
          <div style={{ display: "flex", gap: 6, marginBottom: "var(--space-3)" }}>
            <span className="tag tag-accent">{course.category}</span>
            <span className="tag tag-neutral">{course.level}</span>
          </div>
          <h1 style={{ fontFamily: "var(--font-heading)", fontSize: 32, margin: "0 0 8px" }}>{course.title}</h1>
          <p style={{ opacity: 0.7, margin: "0 0 var(--space-2)" }}>Taught by {course.instructor_name}</p>
          <div style={{ display: "flex", gap: "var(--space-4)", fontSize: 13, opacity: 0.7, marginBottom: "var(--space-5)" }}>
            <span>★ {course.rating ?? "—"} rating</span>
            <span>{course.students} students</span>
            <span>{course.duration_hrs} hours</span>
            <span>{course.lesson_count} lessons</span>
          </div>
          <p style={{ lineHeight: 1.6, margin: "0 0 var(--space-6)" }}>{course.description}</p>

          <h2 style={{ fontFamily: "var(--font-heading)", fontSize: 22, margin: "0 0 var(--space-3)" }}>Curriculum</h2>
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
            {course.lessons.map((lesson) => (
              <div
                key={lesson.id}
                className="card"
                style={{ padding: "var(--space-3) var(--space-4)", display: "flex", alignItems: "center", gap: "var(--space-3)", cursor: "pointer" }}
                onClick={() => navigate(`/courses/${course.id}/lessons/${lesson.id}`)}
              >
                {lesson.done ? <CheckCircleIcon size={18} /> : <CircleIcon size={18} />}
                <div style={{ flex: 1 }}>
                  <p style={{ margin: 0, fontWeight: 600 }}>{lesson.title}</p>
                  <p style={{ margin: 0, fontSize: 12, opacity: 0.6 }}>{lesson.type === "video" ? "Video" : "Reading"} · {lesson.duration} min</p>
                </div>
              </div>
            ))}
            {course.has_quiz && (
              <div
                className="card"
                style={{ padding: "var(--space-3) var(--space-4)", display: "flex", alignItems: "center", gap: "var(--space-3)", cursor: "pointer" }}
                onClick={() => navigate(`/courses/${course.id}/quiz`)}
              >
                <HelpCircleIcon size={18} />
                <div style={{ flex: 1 }}>
                  <p style={{ margin: 0, fontWeight: 600 }}>Final quiz</p>
                  <p style={{ margin: 0, fontSize: 12, opacity: 0.6 }}>
                    {course.quiz_question_count} questions ·{" "}
                    {course.quiz_attempted ? `best score ${course.quiz_best_score}%` : "not attempted yet"}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="card elev-md" style={{ padding: "var(--space-5)", position: "sticky", top: "var(--space-6)" }}>
          {course.enrolled ? (
            <>
              <p style={{ fontSize: 13, opacity: 0.65, margin: "0 0 6px" }}>Your progress</p>
              <div style={{ height: 10, borderRadius: 999, background: "var(--color-neutral-200)", overflow: "hidden", marginBottom: 8 }}>
                <div style={{ height: "100%", width: `${course.progress_pct}%`, background: "var(--color-accent-2-600)" }} />
              </div>
              <p style={{ fontSize: 13, opacity: 0.65, margin: "0 0 var(--space-4)" }}>
                {course.done_count} of {course.lesson_count} lessons complete
              </p>
              <button
                type="button"
                className="btn btn-primary btn-block"
                onClick={() => firstIncomplete && navigate(`/courses/${course.id}/lessons/${firstIncomplete.id}`)}
              >
                Continue learning
              </button>
            </>
          ) : (
            <>
              <p style={{ fontFamily: "var(--font-heading)", fontSize: 24, margin: "0 0 var(--space-2)" }}>Free</p>
              <p style={{ fontSize: 14, opacity: 0.65, margin: "0 0 var(--space-4)" }}>Full access to lessons and the final quiz.</p>
              <button type="button" className="btn btn-primary btn-block" disabled={enrolling} onClick={() => void onEnroll()}>
                {enrolling ? "Enrolling…" : "Enroll now"}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
