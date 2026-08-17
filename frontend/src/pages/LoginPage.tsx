import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { AuthShell, FormError, FormNotice } from "../components/AuthShell";
import { useAuth } from "../auth/AuthContext";
import { resendVerification } from "../lib/authApi";
import { ApiError, sanitizeNextPath } from "../lib/api";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [params] = useSearchParams();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [showResend, setShowResend] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setNotice(null);
    setShowResend(false);
    setSubmitting(true);
    try {
      await login(email, password);
      navigate(sanitizeNextPath(params.get("next")), { replace: true });
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Something went wrong. Please try again.";
      setError(message);
      if (message.toLowerCase().includes("verify")) setShowResend(true);
    } finally {
      setSubmitting(false);
    }
  }

  async function onResend() {
    setNotice(null);
    try {
      const res = await resendVerification(email);
      setNotice(res.message);
    } catch {
      setNotice("If that account needs verification, we've sent a new link.");
    }
  }

  return (
    <AuthShell activeTab="login">
      <form onSubmit={onSubmit}>
        <div className="field" style={{ marginBottom: "var(--space-4)" }}>
          <label htmlFor="af-email">Email address</label>
          <input
            id="af-email"
            className="input"
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <div className="field" style={{ marginBottom: "var(--space-2)" }}>
          <label htmlFor="af-password">Password</label>
          <input
            id="af-password"
            className="input"
            type="password"
            placeholder="At least 10 characters"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <FormNotice message={notice} />
        <FormError message={error} />
        {showResend && (
          <button type="button" className="btn btn-ghost" style={{ marginBottom: "var(--space-4)" }} onClick={() => void onResend()}>
            Resend verification email
          </button>
        )}

        <button type="submit" className="btn btn-primary btn-block" disabled={submitting}>
          {submitting ? "Signing in…" : "Sign in"}
        </button>
      </form>
    </AuthShell>
  );
}
