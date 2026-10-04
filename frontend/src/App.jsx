import { useState } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import Sidebar from "./components/Sidebar.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import CreateUrl from "./pages/CreateUrl.jsx";
import UrlDetails from "./pages/UrlDetails.jsx";
import Routing from "./pages/Routing.jsx";
import Analytics from "./pages/Analytics.jsx";

export default function App() {
  const [menuOpen, setMenuOpen] = useState(false);
  return (
    <div className="shell">
      <Sidebar open={menuOpen} onNavigate={() => setMenuOpen(false)} />
      <div className="main">
        <Navbar onMenu={() => setMenuOpen((o) => !o)} />
        <main className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/create" element={<CreateUrl />} />
            <Route path="/urls/:code" element={<UrlDetails />} />
            <Route path="/routing" element={<Routing />} />
            <Route path="/routing/:code" element={<Routing />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/analytics/:code" element={<Analytics />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}
