import { NavLink, Outlet, useLocation } from "react-router-dom";
import {
  BarChart3,
  Brush,
  Database,
  GitCompare,
  Home,
  LayoutDashboard,
  Lightbulb,
  Sparkles,
  Upload,
} from "lucide-react";
import { ROUTES } from "../constants/routes.js";

const NAV_LINKS = [
  { to: ROUTES.UPLOAD, label: "Upload", icon: Upload },
  { to: ROUTES.DATASETS, label: "Datasets", icon: Database },
  { to: ROUTES.CLEANING, label: "Cleaning", icon: Brush },
  { to: ROUTES.ANALYSIS, label: "Analysis", icon: BarChart3 },
  { to: ROUTES.VISUALIZATION, label: "Visualization", icon: BarChart3 },
  { to: ROUTES.COMPARISON, label: "Comparison", icon: GitCompare },
  { to: ROUTES.INSIGHTS, label: "Insights", icon: Lightbulb },
  { to: ROUTES.DASHBOARD, label: "Dashboard", icon: LayoutDashboard },
];

export default function MainLayout() {
  const location = useLocation();
  const isHome = location.pathname === "/" || location.pathname === "";
  return (
    <div className={`min-h-screen datalens-shell ${isHome ? "home-surface" : "app-surface"} text-neutral-900 dark:text-neutral-100`}>
      <div className="ambient ambient-one" aria-hidden="true" />
      <div className="ambient ambient-two" aria-hidden="true" />
      <div className="ambient-grid" aria-hidden="true" />
      <div className="datalens-orbit" aria-hidden="true" />
      <div className="datalens-node node-a" aria-hidden="true" />
      <div className="datalens-node node-b" aria-hidden="true" />
      <div className="datalens-node node-c" aria-hidden="true" />

      <header className="datalens-header">
        <nav className="datalens-nav">
          <NavLink to={ROUTES.HOME} className="brand-mark" aria-label="DataLens home">
            <span className="brand-icon"><Sparkles className="h-4 w-4" /></span>
            <span className="brand-copy">
              <span className="brand-name">DataLens</span>
              <span className="brand-caption">Data Intelligence</span>
            </span>
          </NavLink>

          <div className="nav-links">
            <NavLink
              to={ROUTES.HOME}
              end
              className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
            >
              <Home className="nav-icon" />
              <span>Home</span>
            </NavLink>

            {NAV_LINKS.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
              >
                <Icon className="nav-icon" />
                <span>{label}</span>
              </NavLink>
            ))}
          </div>

          <div className="nav-status" title="Local workspace">
            <span className="status-dot" />
            <span>Local</span>
          </div>
        </nav>
      </header>

      <main className="datalens-content">
        <Outlet />
      </main>
    </div>
  );
}
