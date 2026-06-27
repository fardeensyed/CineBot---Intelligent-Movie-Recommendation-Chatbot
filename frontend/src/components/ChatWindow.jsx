import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Send, Clapperboard } from 'lucide-react';
import ChatHistory from './ChatHistory';

const generateUUID = () => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
};

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function ChatWindow() {
  const [sessionId, setSessionId] = useState('');
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);

  // Set up session ID and initial greeting
  useEffect(() => {
    const newSessionId = generateUUID();
    setSessionId(newSessionId);
    setMessages([
      {
        id: 'welcome',
        sender: 'bot',
        text: "Hi! I'm CineBot, your intelligent movie recommendation chatbot. Describe your mood, preferred genre, or a rating threshold (e.g. 'I want a funny movie for a lazy Sunday' or 'recommend a thriller with rating above 8'), and I'll find a match for you!",
        movies: []
      }
    ]);
  }, []);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isTyping) return;

    const userText = input.trim();
    setInput('');

    // Add user message to display
    const userMsg = {
      id: generateUUID(),
      sender: 'user',
      text: userText,
      movies: []
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsTyping(true);

    try {
      const response = await axios.post(`${API_BASE}/chat`, {
        session_id: sessionId,
        message: userText
      });

      const botMsg = {
        id: generateUUID(),
        sender: 'bot',
        text: response.data.reply,
        movies: response.data.movie_cards || []
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error(err);
      const errorMsg = {
        id: generateUUID(),
        sender: 'bot',
        text: "I had trouble generating recommendations. Please ensure the backend is running and your Groq API key is valid, then try again.",
        movies: []
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleFeedback = async (title, liked) => {
    try {
      await axios.post(`${API_BASE}/feedback`, {
        session_id: sessionId,
        movie_title: title,
        liked: liked
      });
    } catch (err) {
      console.error("Failed to post feedback:", err);
    }
  };

  return (
    <div className="chat-window">
      <div className="app-header">
        <div className="brand">
          <div className="brand-logo">
            <Clapperboard size={28} />
          </div>
          <h1>Cine<span>Bot</span></h1>
        </div>
        <div className="session-badge" title="Feedback and memory reset if you refresh your browser.">
          Session ID: {sessionId ? sessionId.substring(0, 8) : '...'}
        </div>
      </div>

      <ChatHistory
        messages={messages}
        onFeedback={handleFeedback}
        isTyping={isTyping}
      />

      <div className="chat-input-container">
        <form onSubmit={handleSend} className="chat-form">
          <input
            type="text"
            className="chat-input"
            placeholder="Tell me what you want to watch (mood, genre, ratings)..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isTyping}
            aria-label="Request movies input"
          />
          <button
            type="submit"
            className="send-btn"
            disabled={!input.trim() || isTyping}
            aria-label="Send button"
          >
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
}
