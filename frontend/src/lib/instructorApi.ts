import { apiGet, apiPost, apiPut } from "./api";
import type { AnalyticsOut, CourseDetail, CoursePayload, InstructorCourseListItem, QuizQuestionInstructorOut } from "./types";

export function myCourses(): Promise<InstructorCourseListItem[]> {
  return apiGet("/instructor/courses");
}

export function getMyCourse(courseId: string): Promise<CourseDetail> {
  return apiGet(`/instructor/courses/${courseId}`);
}

export function getMyCourseQuiz(courseId: string): Promise<QuizQuestionInstructorOut[]> {
  return apiGet(`/instructor/courses/${courseId}/quiz`);
}

export function createCourse(payload: CoursePayload): Promise<CourseDetail> {
  return apiPost("/instructor/courses", payload);
}

export function updateCourse(courseId: string, payload: CoursePayload): Promise<CourseDetail> {
  return apiPut(`/instructor/courses/${courseId}`, payload);
}

export function getAnalytics(): Promise<AnalyticsOut> {
  return apiGet("/instructor/analytics");
}
