import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { AuthShell, FormError } from "../components/AuthShell";
import { resetPassword } from "../lib/authApi";
import { ApiError } from "../lib/api";

export function ResetPasswordPage() {
  const [params] = useSearchParams();
  const token = params.get("token") ?? "";

  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }
    setSubmitting(true);
    try {
      await resetPassword(token, password, confirm);
      setDone(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  if (!token) {
    return (
      <AuthShell activeTab="login">
        <p style={{ margin: "0 0 var(--space-4)" }}>This reset link is missing its token.</p>
        <Link to="/forgot-password" className="btn btn-primary btn-block">Request a new link</Link>
      </AuthShell>
    );
  }

  if (done) {
    return (
      <AuthShell activeTab="login">
        <p style={{ margin: "0 0 var(--space-4)" }}>Your password has been reset. You can now sign in.</p>
        <Link to="/login" className="btn btn-primary btn-block">Go to sign in</Link>
      </AuthShell>
    );
  }

  return (
    <AuthShell activeTab="login">
      <form onSubmit={onSubmit}>
        <div className="field" style={{ marginBottom: "var(--space-4)" }}>
          <label htmlFor="rp-password">New password</label>
          <input id="rp-password" className="input" type="password" placeholder="At least 10 characters" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </div>
        <div className="field" style={{ marginBottom: "var(--space-5)" }}>
          <label htmlFor="rp-confirm">Confirm new password</label>
          <input id="rp-confirm" className="input" type="password" placeholder="Repeat your new password" value={confirm} onChange={(e) => setConfirm(e.target.value)} required />
        </div>
        <FormError message={error} />
        <button type="submit" className="btn btn-primary btn-block" disabled={submitting}>
          {submitting ? "Resetting…" : "Reset password"}
        </button>
      </form>
    </AuthShell>
  );
}
