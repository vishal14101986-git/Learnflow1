import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { LogoIcon, SignOutIcon } from "./icons";

function navClass({ isActive }: { isActive: boolean }): string {
  return `btn btn-ghost${isActive ? " on" : ""}`;
}

export function Shell() {
  const { user, logout } = useAuth();

  return (
    <div style={{ minHeight: "100vh", background: "var(--color-bg)", color: "var(--color-text)", fontFamily: "var(--font-body)" }}>
      <div className="nav" style={{ padding: "var(--space-3) var(--space-6)" }}>
        <div className="nav-brand" style={{ display: "flex", alignItems: "center", gap: 8, marginRight: 0 }}>
          <LogoIcon size={22} />
          <span style={{ fontFamily: "var(--font-heading)", fontSize: 19 }}>LearnFlow</span>
        </div>

        <div style={{ marginRight: "auto" }} />

        {user?.role === "learner" && (
          <>
            <NavLink to="/catalog" className={navClass}>Catalog</NavLink>
            <NavLink to="/dashboard" className={navClass}>My progress</NavLink>
          </>
        )}
        {user?.role === "instructor" && (
          <>
            <NavLink to="/instructor/courses" className={navClass}>My courses</NavLink>
            <NavLink to="/instructor/analytics" className={navClass}>Analytics</NavLink>
          </>
        )}

        <div style={{ display: "flex", alignItems: "center", gap: "var(--space-3)" }}>
          <span style={{ fontSize: 14, opacity: 0.7 }}>Hi, {user?.name}</span>
          <button type="button" className="btn-icon" title="Sign out" onClick={() => void logout()}>
            <SignOutIcon size={18} />
          </button>
        </div>
      </div>

      <div style={{ maxWidth: 1180, margin: "0 auto", padding: "var(--space-6)" }}>
        <Outlet />
      </div>
    </div>
  );
}
