// src/components/ChatWindow.jsx
import React, { useState } from 'react';

// New sub-component for displaying sources
function Sources({ chunks }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!chunks || chunks.length === 0) {
    return null;
  }

  return (
    <div className="sources-container">
      <button onClick={() => setIsOpen(!isOpen)} className="sources-button">
        {isOpen ? 'Hide Sources' : 'Show Sources'}
      </button>
      {isOpen && (
        <div className="sources-content">
          <h4>Sources:</h4>
          {chunks.map((chunk, index) => (
            <div key={index} className="source-chunk">
              <p>{chunk}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ChatWindow() {
  const [messages, setMessages] = useState([
    { sender: 'ai', text: 'I have read your document. Ask me anything!' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:5300/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: input }),
      });
      const data = await response.json();

      const aiMessage = { 
        sender: 'ai', 
        text: data.answer || 'Sorry, I encountered an error.',
        sources: data.sources // <-- Store the sources with the message
      };
      setMessages(prev => [...prev, aiMessage]);

    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = { sender: 'ai', text: 'Failed to get a response from the server.' };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleSend();
    }
  };

  return (
    <div className="chat-window">
      <div className="messages-area">
        {messages.map((msg, index) => (
          // We wrap each message in a container for better layout
          <div key={index} className={`message-container ${msg.sender}`}>
            <div className={`message ${msg.sender}`}>
              <p>{msg.text}</p>
            </div>
            {/* If the message is from the AI, show the Sources component */}
            {msg.sender === 'ai' && <Sources chunks={msg.sources} />}
          </div>
        ))}
        {isLoading && <div className="message ai"><p>Thinking...</p></div>}
      </div>
      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask a question..."
          disabled={isLoading}
        />
        <button onClick={handleSend} disabled={isLoading}>
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatWindow;