import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { completeLesson, getCourse } from "../lib/coursesApi";
import type { CourseDetail } from "../lib/types";
import { CheckCircleIcon, CircleIcon, PlayIcon } from "../components/icons";
import { CenteredNote } from "../components/Guards";

export function LessonPlayerPage() {
  const { courseId, lessonId } = useParams<{ courseId: string; lessonId: string }>();
  const navigate = useNavigate();
  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [saving, setSaving] = useState(false);

  const load = useCallback(() => {
    if (!courseId) return;
    getCourse(courseId).then(setCourse);
  }, [courseId]);

  useEffect(() => {
    load();
  }, [load]);

  if (!course) return <CenteredNote text="Loading…" />;

  const idx = course.lessons.findIndex((l) => l.id === lessonId);
  const lesson = idx >= 0 ? course.lessons[idx] : course.lessons[0];
  if (!lesson) return <CenteredNote text="This course has no lessons yet." />;

  const isLast = idx === course.lessons.length - 1;

  async function onCompleteAndNext() {
    setSaving(true);
    try {
      await completeLesson(course!.id, lesson.id);
      if (!isLast) {
        navigate(`/courses/${course!.id}/lessons/${course!.lessons[idx + 1].id}`);
      } else if (course!.has_quiz) {
        navigate(`/courses/${course!.id}/quiz`);
      } else {
        navigate(`/courses/${course!.id}`);
      }
    } finally {
      setSaving(false);
    }
  }

  function onPrev() {
    if (idx > 0) navigate(`/courses/${course!.id}/lessons/${course!.lessons[idx - 1].id}`);
  }

  return (
    <div>
      <button type="button" className="btn btn-ghost" style={{ marginBottom: "var(--space-4)" }} onClick={() => navigate(`/courses/${course.id}`)}>
        &larr; {course.title}
      </button>

      <div style={{ display: "grid", gridTemplateColumns: "280px 1fr", gap: "var(--space-6)", alignItems: "start" }}>
        <div className="card" style={{ padding: "var(--space-3)" }}>
          <p style={{ fontSize: 12, textTransform: "uppercase", letterSpacing: "0.08em", opacity: 0.55, margin: "0 0 var(--space-2)" }}>Lessons</p>
          <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            {course.lessons.map((l) => (
              <button
                key={l.id}
                type="button"
                className={`btn-ghost${l.id === lesson.id ? " on" : ""}`}
                style={{ justifyContent: "flex-start", textAlign: "left", padding: "var(--space-2) var(--space-3)" }}
                onClick={() => navigate(`/courses/${course.id}/lessons/${l.id}`)}
              >
                <span style={{ display: "flex", alignItems: "center", gap: 8, width: "100%" }}>
                  {l.done ? <CheckCircleIcon size={15} /> : <CircleIcon size={15} />}
                  <span style={{ fontSize: 13 }}>{l.title}</span>
                </span>
              </button>
            ))}
          </div>
        </div>

        <div>
          <div style={{ display: "flex", gap: 6, marginBottom: "var(--space-3)" }}>
            <span className="tag tag-outline">{lesson.type === "video" ? "Video" : "Reading"}</span>
            <span className="tag tag-neutral">{lesson.duration} min</span>
          </div>
          <h1 style={{ fontFamily: "var(--font-heading)", fontSize: 28, margin: "0 0 var(--space-4)" }}>{lesson.title}</h1>

          {lesson.type === "video" && (
            <div style={{ height: 320, borderRadius: "var(--radius-lg)", background: "var(--color-neutral-800)", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: "var(--space-5)" }}>
              <PlayIcon size={56} />
            </div>
          )}

          <p style={{ lineHeight: 1.7, fontSize: 16, margin: "0 0 var(--space-6)" }}>{lesson.body}</p>

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "var(--space-3)" }}>
            <button type="button" className="btn btn-secondary" disabled={idx === 0} onClick={onPrev}>
              Previous
            </button>
            <button type="button" className="btn btn-primary" disabled={saving} onClick={() => void onCompleteAndNext()}>
              {isLast ? (course.has_quiz ? "Complete and take quiz" : "Complete course") : "Complete and continue"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
