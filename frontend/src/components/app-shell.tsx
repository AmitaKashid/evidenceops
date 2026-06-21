"use client";

import Link from "next/link";
import type { Route } from "next";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

const navItems: Array<{ href: Route; label: string; detail: string }> = [
  { href: "/", label: "Control room", detail: "Runs and quality" },
  { href: "/runs", label: "Task studio", detail: "Execute and review" },
  { href: "/evaluations", label: "Evaluation lab", detail: "Compare policies" },
  { href: "/architecture", label: "Architecture", detail: "Boundaries and controls" }
];

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Link className="brand" href="/">
          <span className="brand-mark">EO</span>
          <span>
            <strong>EvidenceOps</strong>
            <small>Decision intelligence</small>
          </span>
        </Link>
        <nav aria-label="Primary navigation">
          {navItems.map((item) => {
            const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            return (
              <Link key={item.href} href={item.href} className={`nav-item ${active ? "active" : ""}`}>
                <span>{item.label}</span>
                <small>{item.detail}</small>
              </Link>
            );
          })}
        </nav>
        <div className="sidebar-footer">
          <span className="status-dot" />
          <span>Demo tenant · Read-only workflow</span>
        </div>
      </aside>
      <main className="main-content">{children}</main>
    </div>
  );
}
