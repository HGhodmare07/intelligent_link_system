import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/create", label: "Create URL" },
  { to: "/analytics", label: "Analytics" },
];

export default function Sidebar({ open, onNavigate }) {
  return (
    <aside className={`sidebar ${open ? "sidebar-open" : ""}`}>
      <div className="brand">
        <div className="brand-mark">L</div>
        <div>
          <div className="brand-name">Link Resolver</div>
          <div className="brand-sub">Traffic and security</div>
        </div>
      </div>
      <nav>
        {links.map((l) => (
          <NavLink key={l.to} to={l.to} end={l.end} onClick={onNavigate} className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
            {l.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
