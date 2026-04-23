import { useState, useEffect } from 'react';
import { submitRating } from '../api/client';
import { useAuthStore } from '../store/authStore';
import toast from 'react-hot-toast';

export default function WriteReview({ movieId, existingRating, onSubmit }) {
  const { isAuthenticated } = useAuthStore();
  const [score, setScore] = useState(existingRating?.score || 0);
  const [hovered, setHovered] = useState(0);
  const [title, setTitle] = useState(existingRating?.review_title || '');
  const [text, setText] = useState(existingRating?.review_text || '');
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    if (existingRating) {
      setScore(existingRating.score || 0);
      setTitle(existingRating.review_title || '');
      setText(existingRating.review_text || '');
      setSubmitted(true);
    }
  }, [existingRating]);

  if (!isAuthenticated) {
    return (
      <div className="write-review write-review--guest">
        <p>
          <a href="/login">Sign in</a> to rate and review this movie.
        </p>
      </div>
    );
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (score === 0) { toast.error('Please select a star rating'); return; }
    setLoading(true);
    try {
      const res = await submitRating({
        movie_id: movieId,
        score,
        review_title: title.trim() || null,
        review_text: text.trim() || null,
      });
      toast.success(submitted ? 'Review updated!' : 'Review posted!');
      setSubmitted(true);
      onSubmit && onSubmit(res.data);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to submit review');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="write-review">
      <h3 className="write-review__title">
        {submitted ? '✏️ Update Your Review' : '✍️ Write a Review'}
      </h3>
      <form onSubmit={handleSubmit} className="write-review__form">
        {/* Star Rating Picker */}
        <div className="write-review__stars">
          <label>Your Rating *</label>
          <div className="star-picker">
            {[1,2,3,4,5].map(n => (
              <button
                key={n}
                type="button"
                onMouseEnter={() => setHovered(n)}
                onMouseLeave={() => setHovered(0)}
                onClick={() => setScore(n)}
                style={{
                  fontSize: '2rem',
                  color: (hovered || score) >= n ? '#e2b616' : '#444',
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  padding: '0 2px',
                  transition: 'color 0.15s',
                }}
              >★</button>
            ))}
            {score > 0 && (
              <span style={{ color: '#aaa', fontSize: '0.9rem', marginLeft: '8px' }}>
                {['', 'Awful', 'Poor', 'Average', 'Good', 'Excellent'][score]}
              </span>
            )}
          </div>
        </div>

        {/* Review Title */}
        <div className="form-group">
          <label htmlFor="review-title">Review Title <span style={{color:'#888'}}>(optional)</span></label>
          <input
            id="review-title"
            type="text"
            className="form-input"
            placeholder="Sum up your thoughts in one line..."
            value={title}
            maxLength={150}
            onChange={(e) => setTitle(e.target.value)}
          />
          <span style={{ color: '#888', fontSize: '0.75rem' }}>{title.length}/150</span>
        </div>

        {/* Review Text */}
        <div className="form-group">
          <label htmlFor="review-text">Your Review <span style={{color:'#888'}}>(optional)</span></label>
          <textarea
            id="review-text"
            className="form-input"
            placeholder="What did you think? Would you recommend it?"
            value={text}
            maxLength={2000}
            rows={5}
            onChange={(e) => setText(e.target.value)}
            style={{ resize: 'vertical', minHeight: '120px' }}
          />
          <span style={{ color: '#888', fontSize: '0.75rem' }}>{text.length}/2000</span>
        </div>

        <button 
          type="submit" 
          className="btn-primary" 
          disabled={loading || score === 0}
        >
          {loading ? 'Submitting...' : submitted ? 'Update Review' : 'Post Review'}
        </button>
      </form>
    </div>
  );
}
