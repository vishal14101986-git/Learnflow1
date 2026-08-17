export type UserRole = "learner" | "instructor" | "administrator";
export type UserStatus = "pending_verification" | "active" | "locked" | "suspended" | "deactivated";

export interface UserOut {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  status: UserStatus;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: UserOut;
}

export type LessonType = "video" | "text";
export type QuestionType = "mcq" | "tf" | "short";
export type CourseLevel = "Beginner" | "Intermediate" | "Advanced";

export interface LessonOut {
  id: string;
  title: string;
  type: LessonType;
  duration: number;
  body: string;
  done: boolean;
}

export interface LessonIn {
  id?: string | null;
  title: string;
  type: LessonType;
  duration: number;
  body: string;
}

export interface QuizQuestionOut {
  id: string;
  type: QuestionType;
  text: string;
  options: string[] | null;
}

export interface QuizQuestionInstructorOut extends QuizQuestionOut {
  answer: boolean | number | string;
}

export interface QuizQuestionIn {
  id?: string | null;
  type: QuestionType;
  text: string;
  options: string[] | null;
  answer: boolean | number | string;
}

export interface CourseListItem {
  id: string;
  title: string;
  category: string;
  level: CourseLevel;
  instructor_name: string;
  rating: number | null;
  students: number;
  duration_hrs: number;
  swatch: number;
  lesson_count: number;
  enrolled: boolean;
  progress_pct: number;
}

export interface CourseDetail extends CourseListItem {
  description: string;
  lessons: LessonOut[];
  has_quiz: boolean;
  quiz_question_count: number;
  quiz_attempted: boolean;
  quiz_best_score: number | null;
  done_count: number;
}

export interface CoursePayload {
  title: string;
  category: string;
  level: CourseLevel;
  instructor_name: string;
  duration_hrs: number;
  rating: number | null;
  swatch: number;
  description: string;
  lessons: LessonIn[];
  quiz_questions: QuizQuestionIn[];
}

export interface QuizReviewItem {
  text: string;
  given: string;
  correct: string;
  ok: boolean;
}

export interface QuizSubmitResponse {
  score: number;
  correct_count: number;
  total_count: number;
  passed: boolean;
  review: QuizReviewItem[];
}

export interface DashboardStats {
  stat_enrolled: number;
  stat_completed: number;
  stat_avg_score: number;
  stat_certificates: number;
}

export interface EnrolledCourseOut {
  id: string;
  title: string;
  swatch: number;
  progress_pct: number;
  done_count: number;
  lesson_total: number;
  quiz_attempted: boolean;
  quiz_score: number | null;
  has_certificate: boolean;
}

export interface DashboardOut {
  stats: DashboardStats;
  enrolled_courses: EnrolledCourseOut[];
}

export interface InstructorCourseListItem {
  id: string;
  title: string;
  students: number;
  completion_rate: number;
  avg_quiz_score: number;
  rating: number | null;
  swatch: number;
}

export interface AnalyticsCourseRow {
  id: string;
  title: string;
  students: number;
  completion_rate: number;
  avg_quiz_score: number;
  rating: number | null;
}

export interface AnalyticsOut {
  total_students: number;
  avg_completion_rate: number;
  avg_quiz_score_all: number;
  courses: AnalyticsCourseRow[];
}
