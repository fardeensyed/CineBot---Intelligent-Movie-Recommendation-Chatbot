import React, { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';

export default function ChatHistory({ messages, onFeedback, isTyping }) {
  const scrollRef = useRef(null);

  useEffect(() => {
    // Auto-scroll to bottom of the chat container
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  return (
    <div className="chat-history" ref={scrollRef}>
      {messages.map((msg) => (
        <MessageBubble
          key={msg.id}
          message={msg}
          onFeedback={onFeedback}
        />
      ))}

      {isTyping && (
        <div className="loading-bubble" aria-label="CineBot is thinking">
          <div className="dot" />
          <div className="dot" />
          <div className="dot" />
        </div>
      )}
    </div>
  );
}
