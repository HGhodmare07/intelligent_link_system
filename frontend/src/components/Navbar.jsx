export default function Navbar({ onMenu }) {
  return (
    <header className="navbar">
      <button type="button" className="menu-btn" onClick={onMenu} aria-label="Toggle navigation">
        <span /><span /><span />
      </button>
      <div className="navbar-title">Intelligent Link Resolution and Traffic Analysis System</div>
    </header>
  );
}
