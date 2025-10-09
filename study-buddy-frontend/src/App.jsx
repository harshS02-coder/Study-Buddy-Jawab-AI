// src/App.jsx
import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import ChatWindow from './components/chatWindow'; // Import the new component
import './App.css';

function App() {
  const [isFileUploaded, setIsFileUploaded] = useState(false);

  const handleUploadSuccess = () => {
    setIsFileUploaded(true);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Study Buddy-Jawab AI</h1>
      </header>
      <main>
        {!isFileUploaded ? (
          <FileUpload onUploadSuccess={handleUploadSuccess} />
        ) : (
          // Replace the old div with the ChatWindow component
          <ChatWindow />
        )}
      </main>
    </div>
  );
}

export default App;