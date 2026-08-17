import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { createCourse, getMyCourse, getMyCourseQuiz, updateCourse } from "../lib/instructorApi";
import type { CourseLevel, CoursePayload, LessonType, QuestionType } from "../lib/types";
import { ArrowDownIcon, ArrowUpIcon, TrashIcon } from "../components/icons";
import { CenteredNote } from "../components/Guards";

function uid(): string {
  return Math.random().toString(36).slice(2, 10);
}

interface DraftLesson {
  key: string;
  title: string;
  type: LessonType;
  duration: number;
  body: string;
  videoUrl: string;
}

interface DraftOption {
  key: string;
  value: string;
}

interface DraftQuestion {
  key: string;
  type: QuestionType;
  text: string;
  options: DraftOption[];
  answerIndex: number;
  answerBool: boolean;
  answerShort: string;
}

function blankLesson(): DraftLesson {
  return { key: uid(), title: "New lesson", type: "video", duration: 10, body: "", videoUrl: "" };
}

function blankQuestion(): DraftQuestion {
  return {
    key: uid(),
    type: "mcq",
    text: "New question",
    options: [{ key: uid(), value: "" }, { key: uid(), value: "" }, { key: uid(), value: "" }, { key: uid(), value: "" }],
    answerIndex: 0,
    answerBool: true,
    answerShort: "",
  };
}

export function InstructorCourseBuilderPage() {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  const isEdit = !!courseId;

  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);

  const [title, setTitle] = useState("");
  const [instructorName, setInstructorName] = useState("");
  const [category, setCategory] = useState("Generative AI");
  const [level, setLevel] = useState<CourseLevel>("Beginner");
  const [duration, setDuration] = useState(1);
  const [description, setDescription] = useState("");
  const [lessons, setLessons] = useState<DraftLesson[]>([]);
  const [questions, setQuestions] = useState<DraftQuestion[]>([]);

  useEffect(() => {
    if (!courseId) return;
    Promise.all([getMyCourse(courseId), getMyCourseQuiz(courseId)]).then(([course, quiz]) => {
      setTitle(course.title);
      setInstructorName(course.instructor_name);
      setCategory(course.category);
      setLevel(course.level);
      setDuration(course.duration_hrs);
      setDescription(course.description);
      setLessons(course.lessons.map((l) => ({ key: uid(), title: l.title, type: l.type, duration: l.duration, body: l.body, videoUrl: l.video_url ?? "" })));
      setQuestions(
        quiz.map((q) => ({
          key: uid(),
          type: q.type,
          text: q.text,
          options:
            q.type === "mcq" && q.options
              ? q.options.map((value) => ({ key: uid(), value }))
              : [{ key: uid(), value: "" }, { key: uid(), value: "" }, { key: uid(), value: "" }, { key: uid(), value: "" }],
          answerIndex: q.type === "mcq" && typeof q.answer === "number" ? q.answer : 0,
          answerBool: q.type === "tf" ? Boolean(q.answer) : true,
          answerShort: q.type === "short" ? String(q.answer) : "",
        }))
      );
      setLoading(false);
    });
  }, [courseId]);

  if (loading) return <CenteredNote text="Loading…" />;

  function updateLesson(key: string, patch: Partial<DraftLesson>) {
    setLessons((prev) => prev.map((l) => (l.key === key ? { ...l, ...patch } : l)));
  }
  function moveLesson(key: string, dir: -1 | 1) {
    setLessons((prev) => {
      const i = prev.findIndex((l) => l.key === key);
      const j = i + dir;
      if (i < 0 || j < 0 || j >= prev.length) return prev;
      const copy = [...prev];
      [copy[i], copy[j]] = [copy[j], copy[i]];
      return copy;
    });
  }
  function removeLesson(key: string) {
    setLessons((prev) => prev.filter((l) => l.key !== key));
  }

  function updateQuestion(key: string, patch: Partial<DraftQuestion>) {
    setQuestions((prev) => prev.map((q) => (q.key === key ? { ...q, ...patch } : q)));
  }
  function removeQuestion(key: string) {
    setQuestions((prev) => prev.filter((q) => q.key !== key));
  }
  function updateOption(qKey: string, oKey: string, value: string) {
    setQuestions((prev) =>
      prev.map((q) => (q.key === qKey ? { ...q, options: q.options.map((o) => (o.key === oKey ? { ...o, value } : o)) } : q))
    );
  }

  async function onSave(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      const payload: CoursePayload = {
        title,
        category,
        level,
        instructor_name: instructorName,
        duration_hrs: duration,
        rating: null,
        swatch: 0,
        description,
        lessons: lessons.map((l) => ({
          title: l.title,
          type: l.type,
          duration: l.duration,
          body: l.body,
          video_url: l.type === "video" && l.videoUrl.trim() ? l.videoUrl.trim() : null,
        })),
        quiz_questions: questions.map((q) => {
          if (q.type === "mcq") {
            return { type: "mcq" as const, text: q.text, options: q.options.map((o) => o.value), answer: q.answerIndex };
          }
          if (q.type === "tf") {
            return { type: "tf" as const, text: q.text, options: null, answer: q.answerBool };
          }
          return { type: "short" as const, text: q.text, options: null, answer: q.answerShort };
        }),
      };

      if (isEdit) {
        await updateCourse(courseId!, payload);
      } else {
        await createCourse(payload);
      }
      navigate("/instructor/courses");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div>
      <button type="button" className="btn btn-ghost" style={{ marginBottom: "var(--space-4)" }} onClick={() => navigate("/instructor/courses")}>
        &larr; My courses
      </button>
      <h1 style={{ fontFamily: "var(--font-heading)", fontSize: 28, margin: "0 0 var(--space-5)" }}>
        {isEdit ? "Edit course" : "New course"}
      </h1>

      <form onSubmit={onSave}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--space-4)", marginBottom: "var(--space-4)" }}>
          <div className="field">
            <label>Title</label>
            <input className="input" type="text" value={title} onChange={(e) => setTitle(e.target.value)} required />
          </div>
          <div className="field">
            <label>Instructor name</label>
            <input className="input" type="text" value={instructorName} onChange={(e) => setInstructorName(e.target.value)} required />
          </div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "var(--space-4)", marginBottom: "var(--space-4)" }}>
          <div className="field">
            <label>Category</label>
            <input className="input" type="text" value={category} onChange={(e) => setCategory(e.target.value)} required />
          </div>
          <div className="field">
            <label>Level</label>
            <div className="seg">
              {(["Beginner", "Intermediate", "Advanced"] as CourseLevel[]).map((lv) => (
                <button key={lv} type="button" className={`seg-opt${level === lv ? " on" : ""}`} onClick={() => setLevel(lv)}>
                  {lv}
                </button>
              ))}
            </div>
          </div>
          <div className="field">
            <label>Duration (hours)</label>
            <input className="input" type="number" min={1} value={duration} onChange={(e) => setDuration(Number(e.target.value) || 0)} required />
          </div>
        </div>

        <div className="field" style={{ marginBottom: "var(--space-6)" }}>
          <label>Description</label>
          <textarea className="input" rows={3} value={description} onChange={(e) => setDescription(e.target.value)} />
        </div>

        <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", marginBottom: "var(--space-3)" }}>
          <h2 style={{ fontFamily: "var(--font-heading)", fontSize: 20, margin: 0 }}>Lessons</h2>
          <button type="button" className="btn btn-secondary" onClick={() => setLessons((prev) => [...prev, blankLesson()])}>
            Add lesson
          </button>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-3)", marginBottom: "var(--space-6)" }}>
          {lessons.map((l, i) => (
            <div key={l.key} className="card" style={{ padding: "var(--space-4)" }}>
              <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr auto", gap: "var(--space-3)", marginBottom: "var(--space-3)", alignItems: "end" }}>
                <div className="field" style={{ margin: 0 }}>
                  <label>Lesson title</label>
                  <input className="input" type="text" value={l.title} onChange={(e) => updateLesson(l.key, { title: e.target.value })} />
                </div>
                <div className="field" style={{ margin: 0 }}>
                  <label>Type</label>
                  <div className="seg">
                    <button type="button" className={`seg-opt${l.type === "video" ? " on" : ""}`} onClick={() => updateLesson(l.key, { type: "video" })}>Video</button>
                    <button type="button" className={`seg-opt${l.type === "text" ? " on" : ""}`} onClick={() => updateLesson(l.key, { type: "text" })}>Text</button>
                  </div>
                </div>
                <div className="field" style={{ margin: 0 }}>
                  <label>Minutes</label>
                  <input className="input" type="number" min={1} value={l.duration} onChange={(e) => updateLesson(l.key, { duration: Number(e.target.value) || 0 })} />
                </div>
                <div style={{ display: "flex", gap: 4 }}>
                  <button type="button" className="btn-icon" title="Move up" disabled={i === 0} onClick={() => moveLesson(l.key, -1)}><ArrowUpIcon /></button>
                  <button type="button" className="btn-icon" title="Move down" disabled={i === lessons.length - 1} onClick={() => moveLesson(l.key, 1)}><ArrowDownIcon /></button>
                  <button type="button" className="btn-icon" title="Remove" onClick={() => removeLesson(l.key)}><TrashIcon /></button>
                </div>
              </div>
              {l.type === "video" && (
                <div className="field" style={{ margin: "0 0 var(--space-3)" }}>
                  <label>Video URL</label>
                  <input
                    className="input"
                    type="url"
                    placeholder="https://... (direct .mp4 file, YouTube, or Vimeo link)"
                    value={l.videoUrl}
                    onChange={(e) => updateLesson(l.key, { videoUrl: e.target.value })}
                  />
                </div>
              )}
              <div className="field" style={{ margin: 0 }}>
                <label>Content</label>
                <textarea className="input" rows={2} value={l.body} onChange={(e) => updateLesson(l.key, { body: e.target.value })} />
              </div>
            </div>
          ))}
        </div>

        <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", marginBottom: "var(--space-3)" }}>
          <h2 style={{ fontFamily: "var(--font-heading)", fontSize: 20, margin: 0 }}>Quiz questions</h2>
          <button type="button" className="btn btn-secondary" onClick={() => setQuestions((prev) => [...prev, blankQuestion()])}>
            Add question
          </button>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-3)", marginBottom: "var(--space-6)" }}>
          {questions.map((q) => (
            <div key={q.key} className="card" style={{ padding: "var(--space-4)" }}>
              <div style={{ display: "flex", gap: "var(--space-3)", alignItems: "end", marginBottom: "var(--space-3)" }}>
                <div className="field" style={{ margin: 0, flex: 1 }}>
                  <label>Question text</label>
                  <input className="input" type="text" value={q.text} onChange={(e) => updateQuestion(q.key, { text: e.target.value })} />
                </div>
                <div className="seg">
                  <button type="button" className={`seg-opt${q.type === "mcq" ? " on" : ""}`} onClick={() => updateQuestion(q.key, { type: "mcq" })}>Multiple choice</button>
                  <button type="button" className={`seg-opt${q.type === "tf" ? " on" : ""}`} onClick={() => updateQuestion(q.key, { type: "tf" })}>True / False</button>
                  <button type="button" className={`seg-opt${q.type === "short" ? " on" : ""}`} onClick={() => updateQuestion(q.key, { type: "short" })}>Short answer</button>
                </div>
                <button type="button" className="btn-icon" title="Remove" onClick={() => removeQuestion(q.key)}><TrashIcon /></button>
              </div>

              {q.type === "mcq" && (
                <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
                  {q.options.map((opt, oi) => (
                    <div key={opt.key} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <input type="radio" checked={q.answerIndex === oi} onChange={() => updateQuestion(q.key, { answerIndex: oi })} />
                      <input className="input" type="text" value={opt.value} onChange={(e) => updateOption(q.key, opt.key, e.target.value)} />
                    </div>
                  ))}
                  <p style={{ fontSize: 12, opacity: 0.55, margin: "2px 0 0" }}>Mark the correct option.</p>
                </div>
              )}

              {q.type === "tf" && (
                <div className="seg">
                  <button type="button" className={`seg-opt${q.answerBool ? " on" : ""}`} onClick={() => updateQuestion(q.key, { answerBool: true })}>True is correct</button>
                  <button type="button" className={`seg-opt${!q.answerBool ? " on" : ""}`} onClick={() => updateQuestion(q.key, { answerBool: false })}>False is correct</button>
                </div>
              )}

              {q.type === "short" && (
                <div className="field" style={{ margin: 0 }}>
                  <label>Accepted answer</label>
                  <input className="input" type="text" value={q.answerShort} onChange={(e) => updateQuestion(q.key, { answerShort: e.target.value })} />
                </div>
              )}
            </div>
          ))}
        </div>

        <div style={{ display: "flex", gap: "var(--space-3)" }}>
          <button type="button" className="btn btn-secondary" onClick={() => navigate("/instructor/courses")}>Cancel</button>
          <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? "Saving…" : "Save course"}</button>
        </div>
      </form>
    </div>
  );
}
