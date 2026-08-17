import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { AuthShell } from "../components/AuthShell";
import { verifyEmail } from "../lib/authApi";
import { ApiError } from "../lib/api";

export function VerifyEmailPage() {
  const [params] = useSearchParams();
  const token = params.get("token") ?? "";
  const [status, setStatus] = useState<"pending" | "ok" | "error">("pending");
  const [message, setMessage] = useState("Verifying your email address…");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("This verification link is missing its token.");
      return;
    }
    let cancelled = false;
    verifyEmail(token)
      .then((res) => {
        if (cancelled) return;
        setStatus("ok");
        setMessage(res.message);
      })
      .catch((err) => {
        if (cancelled) return;
        setStatus("error");
        setMessage(err instanceof ApiError ? err.message : "This verification link is invalid or has expired.");
      });
    return () => {
      cancelled = true;
    };
  }, [token]);

  return (
    <AuthShell activeTab="login">
      <p style={{ margin: "0 0 var(--space-4)", opacity: status === "pending" ? 0.7 : 1 }}>{message}</p>
      {status !== "pending" && (
        <Link to="/login" className="btn btn-primary btn-block">
          Go to sign in
        </Link>
      )}
    </AuthShell>
  );
}
