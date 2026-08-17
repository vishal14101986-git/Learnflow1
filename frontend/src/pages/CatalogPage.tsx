import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { listCategories, listCourses } from "../lib/coursesApi";
import type { CourseListItem } from "../lib/types";
import { SearchIcon } from "../components/icons";

const SWATCH_BG = ["var(--color-accent-100)", "var(--color-accent-2-100)"];
const SWATCH_FG = ["var(--color-accent-700)", "var(--color-accent-2-700)"];

function initialsOf(title: string): string {
  const words = title.trim().split(/\s+/).filter(Boolean);
  return ((words[0]?.[0] ?? "?") + (words[1]?.[0] ?? "")).toUpperCase();
}

export function CatalogPage() {
  const navigate = useNavigate();
  const [categories, setCategories] = useState<string[]>(["All"]);
  const [category, setCategory] = useState("All");
  const [search, setSearch] = useState("");
  const [courses, setCourses] = useState<CourseListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listCategories().then(setCategories).catch(() => setCategories(["All"]));
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    const handle = setTimeout(() => {
      listCourses(search, category)
        .then((data) => {
          if (!cancelled) setCourses(data);
        })
        .finally(() => {
          if (!cancelled) setLoading(false);
        });
    }, 200);
    return () => {
      cancelled = true;
      clearTimeout(handle);
    };
  }, [search, category]);

  return (
    <div>
      <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", gap: "var(--space-4)", marginBottom: "var(--space-5)", flexWrap: "wrap" }}>
        <div>
          <h1 style={{ fontFamily: "var(--font-heading)", fontSize: 32, margin: "0 0 4px" }}>Course catalog</h1>
          <p style={{ opacity: 0.65, margin: 0 }}>{courses.length} AI training courses</p>
        </div>
        <div style={{ position: "relative", minWidth: 260 }}>
          <span style={{ position: "absolute", left: 14, top: 12, opacity: 0.5 }}>
            <SearchIcon />
          </span>
          <input
            className="input"
            style={{ paddingLeft: 38 }}
            type="text"
            placeholder="Search courses or instructors"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div style={{ display: "flex", gap: "var(--space-2)", marginBottom: "var(--space-6)", flexWrap: "wrap" }}>
        {categories.map((cat) => (
          <button
            key={cat}
            type="button"
            className={`tag tag-outline${cat === category ? " on" : ""}`}
            style={{ cursor: "pointer", border: "none" }}
            onClick={() => setCategory(cat)}
          >
            {cat}
          </button>
        ))}
      </div>

      {loading ? (
        <p style={{ opacity: 0.6 }}>Loading courses…</p>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "var(--space-5)" }}>
          {courses.map((course) => (
            <div key={course.id} className="card elev-sm" style={{ padding: 0, overflow: "hidden", display: "flex", flexDirection: "column" }}>
              <div style={{ height: 120, background: SWATCH_BG[course.swatch % 2], display: "flex", alignItems: "center", justifyContent: "center" }}>
                <span style={{ fontFamily: "var(--font-heading)", fontSize: 34, color: SWATCH_FG[course.swatch % 2] }}>
                  {initialsOf(course.title)}
                </span>
              </div>
              <div style={{ padding: "var(--space-4)", display: "flex", flexDirection: "column", gap: "var(--space-2)", flex: 1 }}>
                <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                  <span className="tag tag-outline">{course.category}</span>
                  <span className="tag tag-neutral">{course.level}</span>
                </div>
                <h3 className="card-title" style={{ margin: 0, fontSize: 18 }}>{course.title}</h3>
                <p style={{ fontSize: 13, opacity: 0.65, margin: 0 }}>by {course.instructor_name}</p>
                <div style={{ display: "flex", gap: "var(--space-3)", fontSize: 12, opacity: 0.65, marginTop: 2 }}>
                  <span>★ {course.rating ?? "—"}</span>
                  <span>{course.students} students</span>
                  <span>{course.duration_hrs}h</span>
                </div>
                <button
                  type="button"
                  className="btn btn-primary btn-block"
                  style={{ marginTop: "auto" }}
                  onClick={() => navigate(`/courses/${course.id}`)}
                >
                  {course.enrolled ? (course.progress_pct === 100 ? "Review course" : "Continue") : "View course"}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
