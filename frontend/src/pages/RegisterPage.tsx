import { useState } from "react";
import { Link } from "react-router-dom";
import { AuthShell, FormError } from "../components/AuthShell";
import { register } from "../lib/authApi";
import { ApiError } from "../lib/api";
import type { UserRole } from "../lib/types";

export function RegisterPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [role, setRole] = useState<UserRole>("learner");
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
      await register({ name, email, password, confirm_password: confirm, role });
      setDone(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  if (done) {
    return (
      <AuthShell activeTab="register">
        <p style={{ margin: 0 }}>
          If that email address is available, we've created your account — check your inbox for a verification
          link before signing in.
        </p>
        <Link to="/login" className="btn btn-primary btn-block" style={{ marginTop: "var(--space-4)" }}>
          Back to sign in
        </Link>
      </AuthShell>
    );
  }

  return (
    <AuthShell activeTab="register">
      <form onSubmit={onSubmit}>
        <div className="field" style={{ marginBottom: "var(--space-4)" }}>
          <label htmlFor="af-name">Full name</label>
          <input id="af-name" className="input" type="text" placeholder="Ada Lovelace" value={name} onChange={(e) => setName(e.target.value)} required />
        </div>

        <div className="field" style={{ marginBottom: "var(--space-4)" }}>
          <label htmlFor="af-email">Email address</label>
          <input id="af-email" className="input" type="email" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </div>

        <div className="field" style={{ marginBottom: "var(--space-2)" }}>
          <label htmlFor="af-password">Password</label>
          <input id="af-password" className="input" type="password" placeholder="At least 10 characters" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </div>
        <p style={{ fontSize: 12, opacity: 0.6, margin: "0 0 var(--space-4)" }}>Use 10+ characters. Avoid common passwords.</p>

        <div className="field" style={{ marginBottom: "var(--space-4)" }}>
          <label htmlFor="af-confirm">Confirm password</label>
          <input id="af-confirm" className="input" type="password" placeholder="Repeat your password" value={confirm} onChange={(e) => setConfirm(e.target.value)} required />
        </div>

        <div className="field" style={{ marginBottom: "var(--space-5)" }}>
          <label>Join as</label>
          <div className="seg">
            <button type="button" className={`seg-opt${role === "learner" ? " on" : ""}`} onClick={() => setRole("learner")}>Learner</button>
            <button type="button" className={`seg-opt${role === "instructor" ? " on" : ""}`} onClick={() => setRole("instructor")}>Instructor</button>
          </div>
        </div>

        <FormError message={error} />

        <button type="submit" className="btn btn-primary btn-block" disabled={submitting}>
          {submitting ? "Creating account…" : "Create account"}
        </button>
      </form>
    </AuthShell>
  );
}
