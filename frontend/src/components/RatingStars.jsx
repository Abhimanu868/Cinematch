import { useState } from 'react';
import { submitRating } from '../api/client';
import toast from 'react-hot-toast';

export default function RatingStars({ movieId, currentRating, onRate, size = 'md' }) {
  const [hovered, setHovered] = useState(0);
  const [loading, setLoading] = useState(false);
  const active = hovered || currentRating || 0;

  const handleRate = async (score) => {
    if (loading) return;
    setLoading(true);
    try {
      await submitRating({ movie_id: movieId, score });
      toast.success(`Rated ${score} ⭐`);
      if (onRate) onRate(movieId, score);
    } catch (err) {
      toast.error('Sign in to rate movies');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`rating-stars size-${size}`} onMouseLeave={() => setHovered(0)}>
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          className={`star ${active >= star ? 'filled' : ''} ${loading ? 'disabled' : ''}`}
          onMouseEnter={() => setHovered(star)}
          onClick={() => handleRate(star)}
          aria-label={`Rate ${star} star`}
          disabled={loading}
        >
          ★
        </button>
      ))}
      {currentRating && <span className="rating-value">{currentRating}/5</span>}
    </div>
  );
}
