import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, Star } from 'lucide-react';

export default function MovieCard({ movie, onFeedback }) {
  const [feedback, setFeedback] = useState(null); // 'like' | 'dislike' | null

  const handleFeedback = (liked) => {
    const type = liked ? 'like' : 'dislike';
    if (feedback === type) {
      // Toggle off behavior
      setFeedback(null);
      return;
    }
    setFeedback(type);
    if (onFeedback) {
      onFeedback(movie.title, liked);
    }
  };

  return (
    <div className="movie-card">
      <div className="movie-card-header">
        <h3 className="movie-title">{movie.title}</h3>
        <div className="movie-rating">
          <Star size={14} fill="#ffc107" stroke="#ffc107" />
          <span>{movie.rating ? movie.rating.toFixed(1) : 'N/A'}</span>
        </div>
      </div>

      <div className="movie-meta">
        <span className="movie-genre">{movie.genre}</span>
        <span className="movie-year">{movie.year}</span>
      </div>

      <p className="movie-overview" title={movie.overview}>
        {movie.overview}
      </p>

      {movie.justification && (
        <div className="movie-justification">
          {movie.justification}
        </div>
      )}

      <div className="movie-actions">
        <button
          className={`feedback-btn liked ${feedback === 'like' ? 'active' : ''}`}
          onClick={() => handleFeedback(true)}
          title="Recommend more like this"
          aria-label="Thumbs Up"
        >
          <ThumbsUp size={16} />
        </button>
        <button
          className={`feedback-btn disliked ${feedback === 'dislike' ? 'active' : ''}`}
          onClick={() => handleFeedback(false)}
          title="Don't recommend this again"
          aria-label="Thumbs Down"
        >
          <ThumbsDown size={16} />
        </button>
      </div>
    </div>
  );
}
