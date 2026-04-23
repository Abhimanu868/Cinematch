import { useState, useEffect, useCallback } from 'react';
import { getMovieReviews } from '../api/client';
import ReviewCard from './ReviewCard';

export default function ReviewsList({ movieId, refreshTrigger }) {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchReviews = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getMovieReviews(movieId);
      setReviews(res.data);
    } catch {
      setReviews([]);
    } finally {
      setLoading(false);
    }
  }, [movieId]);

  useEffect(() => {
    fetchReviews();
  }, [fetchReviews, refreshTrigger]);

  const handleUpdate = (updatedReview) => {
    setReviews(prev => 
      prev.map(r => r.id === updatedReview.id ? { ...r, ...updatedReview } : r)
    );
  };

  const handleDelete = (deletedId) => {
    setReviews(prev => prev.filter(r => r.id !== deletedId));
  };

  if (loading) {
    return (
      <div className="reviews-loading">
        {[1,2,3].map(i => (
          <div key={i} className="review-card review-card--skeleton" 
               style={{ height: '120px', background: '#1a1a2e', borderRadius: '8px', marginBottom: '12px', opacity: 0.5 }} />
        ))}
      </div>
    );
  }

  if (reviews.length === 0) {
    return (
      <div className="reviews-empty">
        <p style={{ color: '#888', textAlign: 'center', padding: '32px 0' }}>
          🎬 No reviews yet. Be the first to review this movie!
        </p>
      </div>
    );
  }

  return (
    <div className="reviews-list">
      <p className="reviews-count" style={{ color: '#aaa', marginBottom: '16px' }}>
        {reviews.length} {reviews.length === 1 ? 'review' : 'reviews'}
      </p>
      {reviews.map(review => (
        <ReviewCard
          key={review.id}
          review={review}
          onUpdate={handleUpdate}
          onDelete={handleDelete}
        />
      ))}
    </div>
  );
}
