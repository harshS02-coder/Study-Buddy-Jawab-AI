import '../modules/NavbarCss.css';

function Navbar({ activeMode, setActiveMode, theme, setTheme }) {
  return (
    <header className="App-header">
      {/* Brand */}
      <div className="brand">
        <span className="brand-icon" aria-hidden>
          🤖
        </span>
        <div className="brand-text">
          <h1 className="title">Jawab AI</h1>
          <p className="subtitle">
            {activeMode === 'study'
              ? 'Your AI study companion'
              : activeMode === 'invoice'
              ? 'Smart invoice intelligence'
              : 'AI for everything'}
          </p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="nav-tabs">
        <button
          className={`nav-tab ${activeMode === 'study' ? 'active' : ''}`}
          onClick={() => setActiveMode('study')}
        >
          📚 Study Buddy
        </button>

        <button
          className={`nav-tab ${activeMode === 'invoice' ? 'active' : ''}`}
          onClick={() => setActiveMode('invoice')}
        >
          🧾 Invoices
        </button>

        <button className="nav-tab disabled" title="Coming soon">
          🚀 More
        </button>
      </nav>

      {/* Actions */}
      <div className="header-actions">
        <button
          className="icon-btn"
          title="Toggle theme"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
        >
          {theme === 'dark' ? '🌙 Dark' : '☀️ Light'}
        </button>
      </div>
    </header>
  );
}

export default Navbar;
