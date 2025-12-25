// src/App.jsx
import React, { useEffect, useState } from 'react';
import FileUpload from './components/FileUpload';
import ChatWindow from './components/chatWindow';
import Navbar from './components/Navbar';
import MainContent from './components/MainContent';
import './App.css';

function App() {
  const [isFileUploaded, setIsFileUploaded] = useState(false);
  const [activeMode, setActiveMode] = useState('study');

  const [theme, setTheme] = useState(() => {
    const stored = typeof window !== 'undefined' ? localStorage.getItem('theme') : null;
    if (stored === 'light' || stored === 'dark') return stored;
    const prefersDark = typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    return prefersDark ? 'dark' : 'light';
  });

  useEffect(() => {
    document.body.classList.toggle('theme-dark', theme === 'dark');
    localStorage.setItem('theme', theme);
  }, [theme]);

  const handleUploadSuccess = () => {
    setIsFileUploaded(true);
  };

  // const handleNewDocument = () => {
  //   window.location.reload();
  // };

  return (
    <div className="App">
      {/* <header className="App-header">
        <div className="brand">
          <span className="brand-icon" aria-hidden>
            📚
          </span>
          <div className="brand-text">
            <h1 className="title">Study Buddy · Jawab AI</h1>
            <p className="subtitle">Upload notes, ask questions, and learn faster</p>
          </div>
        </div>

        <div className="header-actions">
          <button
            className="icon-btn"
            title="Toggle theme"
            aria-label="Toggle theme"
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          >
            {theme === 'dark' ? '🌙 Dark' : '☀️ Light'}
          </button>
          {isFileUploaded && (
            <button onClick={handleNewDocument} className="action-btn">
              Upload New Document
            </button>
          )}
        </div>
      </header> */}

      <Navbar
        activeMode={activeMode}
        setActiveMode={setActiveMode}
        theme={theme}
        setTheme={setTheme}
      />


      {/* <main className="content">
        {!isFileUploaded ? (
          <div className="grid">
            <section className="glass-card upload-card">
              <h2 className="section-title">Get Started</h2>
              <p className="section-help">Drop a PDF or click to select</p>
              <FileUpload onUploadSuccess={handleUploadSuccess} />
              <div className="feature-badges">
                <span className="badge">PDF</span>
                <span className="badge">Fast RAG</span>
                <span className="badge">Sources</span>
              </div>
            </section>

            <aside className="glass-card info-card">
              <h3 className="info-title">What you can do</h3>
              <ul className="info-list">
                <li>Summarize chapters and key concepts</li>
                <li>Ask targeted questions about any section</li>
                <li>See cited source snippets for each answer</li>
              </ul>
              <div className="tip">
                Pro tip: Ask specific questions like “Explain theorem 2.3 with an example”.
              </div>
            </aside>
          </div>
        ) : (
          <section className="glass-card chat-card">
            <div className="chat-header">
              <h2 className="section-title">Your Study Session</h2>
              <p className="section-help">Ask anything from the uploaded document</p>
            </div>
            <ChatWindow />
          </section>
        )}
      </main> */}
      <MainContent 
        isFileUploaded={isFileUploaded}
        handleUploadSuccess={handleUploadSuccess}
        activeMode={activeMode}
      />

      <footer className="App-footer">
        <span>Built for focused learning • Stay curious ✨</span>
      </footer>
    </div>
  );
}

export default App;