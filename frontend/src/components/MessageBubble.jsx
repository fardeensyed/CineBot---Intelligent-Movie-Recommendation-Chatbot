import React from 'react';
import MovieCard from './MovieCard';

export default function MessageBubble({ message, onFeedback }) {
  const isUser = message.sender === 'user';

  return (
    <div className={`message-wrapper ${isUser ? 'user' : 'bot'}`}>
      <div className="message-bubble">
        {message.text}
      </div>

      {!isUser && message.movies && message.movies.length > 0 && (
        <div className="cards-container">
          {message.movies.map((movie, idx) => (
            <MovieCard
              key={`${movie.title}-${idx}`}
              movie={movie}
              onFeedback={onFeedback}
            />
          ))}
        </div>
      )}
    </div>
  );
}
