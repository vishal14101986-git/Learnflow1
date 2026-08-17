import { Navigate, useLocation, useNavigate, useParams } from "react-router-dom";
import type { QuizSubmitResponse } from "../lib/types";

interface LocationState {
  result: QuizSubmitResponse;
  courseTitle: string;
}

export function QuizResultPage() {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as LocationState | null;

  if (!state?.result || !courseId) {
    return <Navigate to={`/courses/${courseId}`} replace />;
  }

  const { result, courseTitle } = state;
  const color = result.passed ? "var(--color-accent-2-700)" : "var(--color-accent-700)";

  return (
    <div style={{ maxWidth: 680 }}>
      <div className="card elev-md" style={{ padding: "var(--space-6)", textAlign: "center", marginBottom: "var(--space-5)" }}>
        <p style={{ fontSize: 12, textTransform: "uppercase", letterSpacing: "0.08em", opacity: 0.55, margin: "0 0 var(--space-2)" }}>{courseTitle}</p>
        <p style={{ fontFamily: "var(--font-heading)", fontSize: 48, margin: 0, color }}>{result.score}%</p>
        <p style={{ margin: "var(--space-2) 0 var(--space-4)" }}>
          {result.correct_count} of {result.total_count} questions correct
        </p>
        <span className={`tag ${result.passed ? "tag-accent-2" : "tag-accent"}`}>{result.passed ? "Passed" : "Not passed yet"}</span>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-3)", marginBottom: "var(--space-5)" }}>
        {result.review.map((r, i) => (
          <div key={i} className="card" style={{ padding: "var(--space-4)" }}>
            <p style={{ fontWeight: 600, margin: "0 0 var(--space-2)" }}>{r.text}</p>
            <p style={{ fontSize: 13, margin: "0 0 4px" }}>Your answer: {r.given}</p>
            <p style={{ fontSize: 13, margin: 0, opacity: 0.7 }}>Correct answer: {r.correct}</p>
            <span className={`tag ${r.ok ? "tag-accent-2" : "tag-neutral"}`} style={{ marginTop: "var(--space-2)", display: "inline-block" }}>
              {r.ok ? "Correct" : "Incorrect"}
            </span>
          </div>
        ))}
      </div>

      <div style={{ display: "flex", gap: "var(--space-3)" }}>
        <button type="button" className="btn btn-secondary" onClick={() => navigate(`/courses/${courseId}/quiz`)}>
          Retake quiz
        </button>
        <button type="button" className="btn btn-primary" onClick={() => navigate(`/courses/${courseId}`)}>
          Back to course
        </button>
      </div>
    </div>
  );
}
