import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getCourse, getQuiz, submitQuiz } from "../lib/coursesApi";
import type { CourseDetail, QuizQuestionOut } from "../lib/types";
import { CenteredNote } from "../components/Guards";

export function QuizPage() {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [questions, setQuestions] = useState<QuizQuestionOut[] | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!courseId) return;
    getCourse(courseId).then(setCourse);
    getQuiz(courseId).then(setQuestions);
  }, [courseId]);

  if (!course || !questions) return <CenteredNote text="Loading…" />;

  function setAnswer(questionId: string, value: string) {
    setAnswers((prev) => ({ ...prev, [questionId]: value }));
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      const payload = Object.entries(answers).map(([question_id, value]) => ({ question_id, value }));
      const result = await submitQuiz(course!.id, payload);
      navigate(`/courses/${course!.id}/quiz/result`, { state: { result, courseTitle: course!.title } });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <button type="button" className="btn btn-ghost" style={{ marginBottom: "var(--space-4)" }} onClick={() => navigate(`/courses/${course.id}`)}>
        &larr; {course.title}
      </button>
      <h1 style={{ fontFamily: "var(--font-heading)", fontSize: 28, margin: "0 0 4px" }}>Final quiz</h1>
      <p style={{ opacity: 0.65, margin: "0 0 var(--space-6)" }}>{questions.length} questions</p>

      <form onSubmit={onSubmit} style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)", maxWidth: 680 }}>
        {questions.map((q, i) => (
          <div key={q.id} className="card" style={{ padding: "var(--space-4)" }}>
            <p style={{ fontWeight: 600, margin: "0 0 var(--space-3)" }}>
              {i + 1}. {q.text}
            </p>

            {q.type === "mcq" && (
              <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
                {(q.options ?? []).map((opt, oi) => (
                  <label key={oi} className="radio">
                    <input type="radio" name={q.id} checked={answers[q.id] === String(oi)} onChange={() => setAnswer(q.id, String(oi))} />
                    <span className="dot" />
                    {opt}
                  </label>
                ))}
              </div>
            )}

            {q.type === "tf" && (
              <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
                <label className="radio">
                  <input type="radio" name={q.id} checked={answers[q.id] === "true"} onChange={() => setAnswer(q.id, "true")} />
                  <span className="dot" />
                  True
                </label>
                <label className="radio">
                  <input type="radio" name={q.id} checked={answers[q.id] === "false"} onChange={() => setAnswer(q.id, "false")} />
                  <span className="dot" />
                  False
                </label>
              </div>
            )}

            {q.type === "short" && (
              <input
                className="input"
                type="text"
                placeholder="Your answer"
                value={answers[q.id] ?? ""}
                onChange={(e) => setAnswer(q.id, e.target.value)}
              />
            )}
          </div>
        ))}
        <button type="submit" className="btn btn-primary btn-block" disabled={submitting}>
          {submitting ? "Submitting…" : "Submit quiz"}
        </button>
      </form>
    </div>
  );
}
