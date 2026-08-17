import { Link, useNavigate } from "react-router-dom";
import type { ReactNode } from "react";
import { LogoIcon } from "./icons";

export function AuthShell({ activeTab, children }: { activeTab: "login" | "register"; children: ReactNode }) {
  const navigate = useNavigate();

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", padding: "var(--space-6)" }}>
      <div style={{ width: "100%", maxWidth: 420 }}>
        <div style={{ textAlign: "center", marginBottom: "var(--space-6)" }}>
          <div style={{ display: "inline-flex", alignItems: "center", gap: 10 }}>
            <LogoIcon size={28} />
            <span style={{ fontFamily: "var(--font-heading)", fontSize: 28, color: "var(--color-text)" }}>LearnFlow</span>
          </div>
          <p style={{ margin: "var(--space-2) 0 0", opacity: 0.65 }}>AI training &amp; development, one lesson at a time.</p>
        </div>

        <div className="card elev-md" style={{ padding: "var(--space-6)" }}>
          <div className="seg" style={{ marginBottom: "var(--space-5)" }}>
            <button
              type="button"
              className={`seg-opt${activeTab === "login" ? " on" : ""}`}
              onClick={() => navigate("/login")}
            >
              Sign in
            </button>
            <button
              type="button"
              className={`seg-opt${activeTab === "register" ? " on" : ""}`}
              onClick={() => navigate("/register")}
            >
              Register
            </button>
          </div>

          {children}
        </div>
        <p style={{ textAlign: "center", fontSize: 12, opacity: 0.5, marginTop: "var(--space-4)" }}>
          Need to reset your password? <Link to="/forgot-password">Reset it here</Link>.
        </p>
      </div>
    </div>
  );
}

export function FormError({ message }: { message: string | null }) {
  if (!message) return null;
  return (
    <p
      style={{
        color: "var(--color-accent-700)",
        background: "var(--color-accent-100)",
        borderRadius: "var(--radius-lg)",
        padding: "var(--space-3)",
        fontSize: 14,
        margin: "0 0 var(--space-4)",
      }}
    >
      {message}
    </p>
  );
}

export function FormNotice({ message }: { message: string | null }) {
  if (!message) return null;
  return (
    <p
      style={{
        color: "var(--color-accent-2-800)",
        background: "var(--color-accent-2-100)",
        borderRadius: "var(--radius-lg)",
        padding: "var(--space-3)",
        fontSize: 14,
        margin: "0 0 var(--space-4)",
      }}
    >
      {message}
    </p>
  );
}
