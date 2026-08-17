import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth/AuthContext";
import { RequireAuth, RequireRole, CenteredNote } from "./components/Guards";
import { Shell } from "./components/Shell";

import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { VerifyEmailPage } from "./pages/VerifyEmailPage";
import { ForgotPasswordPage } from "./pages/ForgotPasswordPage";
import { ResetPasswordPage } from "./pages/ResetPasswordPage";

import { CatalogPage } from "./pages/CatalogPage";
import { CourseDetailPage } from "./pages/CourseDetailPage";
import { LessonPlayerPage } from "./pages/LessonPlayerPage";
import { QuizPage } from "./pages/QuizPage";
import { QuizResultPage } from "./pages/QuizResultPage";
import { DashboardPage } from "./pages/DashboardPage";

import { InstructorCourseListPage } from "./pages/InstructorCourseListPage";
import { InstructorCourseBuilderPage } from "./pages/InstructorCourseBuilderPage";
import { AnalyticsPage } from "./pages/AnalyticsPage";

function Home() {
  const { user, loading } = useAuth();
  if (loading) return <CenteredNote text="Loading…" />;
  if (!user) return <Navigate to="/login" replace />;
  return <Navigate to={user.role === "instructor" ? "/instructor/courses" : "/catalog"} replace />;
}

function RedirectIfAuthed({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <CenteredNote text="Loading…" />;
  if (user) return <Navigate to={user.role === "instructor" ? "/instructor/courses" : "/catalog"} replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Home />} />

          <Route path="/login" element={<RedirectIfAuthed><LoginPage /></RedirectIfAuthed>} />
          <Route path="/register" element={<RedirectIfAuthed><RegisterPage /></RedirectIfAuthed>} />
          <Route path="/verify-email" element={<VerifyEmailPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />

          <Route element={<RequireAuth />}>
            <Route element={<Shell />}>
              <Route path="/catalog" element={<CatalogPage />} />
              <Route path="/courses/:courseId" element={<CourseDetailPage />} />
              <Route path="/courses/:courseId/lessons/:lessonId" element={<LessonPlayerPage />} />
              <Route path="/courses/:courseId/quiz" element={<QuizPage />} />
              <Route path="/courses/:courseId/quiz/result" element={<QuizResultPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />

              <Route element={<RequireRole role="instructor" />}>
                <Route path="/instructor/courses" element={<InstructorCourseListPage />} />
                <Route path="/instructor/courses/new" element={<InstructorCourseBuilderPage />} />
                <Route path="/instructor/courses/:courseId/edit" element={<InstructorCourseBuilderPage />} />
                <Route path="/instructor/analytics" element={<AnalyticsPage />} />
              </Route>
            </Route>
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
