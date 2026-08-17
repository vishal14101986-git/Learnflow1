import { useState } from "react";
import { Link } from "react-router-dom";
import { AuthShell } from "../components/AuthShell";
import { forgotPassword } from "../lib/authApi";

export function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await forgotPassword(email);
      setMessage(res.message);
    } catch {
      setMessage("If an account exists for that address, we've sent password reset instructions.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AuthShell activeTab="login">
      {message ? (
        <>
          <p style={{ margin: "0 0 var(--space-4)" }}>{message}</p>
          <Link to="/login" className="btn btn-primary btn-block">Back to sign in</Link>
        </>
      ) : (
        <form onSubmit={onSubmit}>
          <p style={{ margin: "0 0 var(--space-4)", opacity: 0.75 }}>
            Enter the email address on your account and we'll send you a link to reset your password.
          </p>
          <div className="field" style={{ marginBottom: "var(--space-5)" }}>
            <label htmlFor="fp-email">Email address</label>
            <input id="fp-email" className="input" type="email" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <button type="submit" className="btn btn-primary btn-block" disabled={submitting}>
            {submitting ? "Sending…" : "Send reset link"}
          </button>
        </form>
      )}
    </AuthShell>
  );
}
