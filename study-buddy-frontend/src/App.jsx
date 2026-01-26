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
  const [documentId, setDocumentId] = useState(null);

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

  const handleUploadSuccess = (documentId) => {
    setIsFileUploaded(true);
    setDocumentId(documentId);
  };

  const handleNewDocument = () => {
    // Reset to upload view
    setIsFileUploaded(false);
  };

  return (
    <div className="App">
      <Navbar
        activeMode={activeMode}
        setActiveMode={setActiveMode}
        theme={theme}
        setTheme={setTheme}
      />
      <MainContent 
        isFileUploaded={isFileUploaded}
        handleUploadSuccess={handleUploadSuccess}
        onUploadNewDocument={handleNewDocument}
        activeMode={activeMode}
        documentId={documentId}
      />

      <footer className="App-footer">
        <span>Built for focused learning • Stay curious ✨</span>
      </footer>
    </div>
  );
}

export default App;