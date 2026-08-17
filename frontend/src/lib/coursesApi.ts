import { apiGet, apiPost } from "./api";
import type { CourseDetail, CourseListItem, DashboardOut, QuizQuestionOut, QuizSubmitResponse } from "./types";

export function listCourses(search: string, category: string): Promise<CourseListItem[]> {
  const params = new URLSearchParams();
  if (search) params.set("q", search);
  if (category && category !== "All") params.set("category", category);
  const qs = params.toString();
  return apiGet(`/courses${qs ? `?${qs}` : ""}`);
}

export function listCategories(): Promise<string[]> {
  return apiGet("/courses/categories");
}

export function getCourse(courseId: string): Promise<CourseDetail> {
  return apiGet(`/courses/${courseId}`);
}

export function getQuiz(courseId: string): Promise<QuizQuestionOut[]> {
  return apiGet(`/courses/${courseId}/quiz`);
}

export function enroll(courseId: string): Promise<{ message: string }> {
  return apiPost(`/courses/${courseId}/enroll`);
}

export function completeLesson(courseId: string, lessonId: string): Promise<{ message: string }> {
  return apiPost(`/courses/${courseId}/lessons/${lessonId}/complete`);
}

export function submitQuiz(
  courseId: string,
  answers: { question_id: string; value: string }[]
): Promise<QuizSubmitResponse> {
  return apiPost(`/courses/${courseId}/quiz/submit`, { answers });
}

export function getDashboard(): Promise<DashboardOut> {
  return apiGet("/me/dashboard");
}
