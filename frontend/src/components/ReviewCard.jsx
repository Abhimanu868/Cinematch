import { useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { updateRating, deleteRating } from '../api/client';
import toast from 'react-hot-toast';

const STAR = '★';
const EMPTY_STAR = '☆';

function StarDisplay({ score }) {
  const full = Math.floor(score);
  const stars = Array.from({ length: 5 }, (_, i) => i < full ? STAR : EMPTY_STAR);
  return (
    <span className="review-stars" style={{ color: '#e2b616', fontSize: '1rem' }}>
      {stars.join('')} <span style={{ color: '#aaa', fontSize: '0.85rem' }}>({score}/5)</span>
    </span>
  );
}

export default function ReviewCard({ review, onUpdate, onDelete }) {
  const { user, isAuthenticated } = useAuthStore();
  const [editing, setEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(review.review_title || '');
  const [editText, setEditText] = useState(review.review_text || '');
  const [editScore, setEditScore] = useState(review.score);
  const [loading, setLoading] = useState(false);

  const isOwner = isAuthenticated && user?.id === review.user_id;

  const formatDate = (dateStr) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  };

  const handleSave = async () => {
    if (!editText.trim()) { toast.error('Review text cannot be empty'); return; }
    setLoading(true);
    try {
      const res = await updateRating(review.id, {
        score: editScore,
        review_title: editTitle.trim() || null,
        review_text: editText.trim(),
      });
      toast.success('Review updated');
      setEditing(false);
      onUpdate && onUpdate(res.data);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to update review');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Delete your review?')) return;
    setLoading(true);
    try {
      await deleteRating(review.id);
      toast.success('Review deleted');
      onDelete && onDelete(review.id);
    } catch (err) {
      toast.error('Failed to delete review');
    } finally {
      setLoading(false);
    }
  };

  if (editing) {
    return (
      <div className="review-card review-card--editing">
        <div className="review-edit-score">
          <label>Your Rating:</label>
          <div className="star-input">
            {[1,2,3,4,5].map(n => (
              <button
                key={n}
                type="button"
                className={`star-btn ${editScore >= n ? 'active' : ''}`}
                onClick={() => setEditScore(n)}
                style={{ 
                  color: editScore >= n ? '#e2b616' : '#555', 
                  fontSize: '1.5rem', 
                  background: 'none', 
                  border: 'none', 
                  cursor: 'pointer' 
                }}
              >★</button>
            ))}
          </div>
        </div>
        <input
          className="form-input"
          placeholder="Review title (optional)"
          value={editTitle}
          maxLength={150}
          onChange={(e) => setEditTitle(e.target.value)}
          style={{ marginBottom: '8px' }}
        />
        <textarea
          className="form-input review-textarea"
          placeholder="Write your review..."
          value={editText}
          maxLength={2000}
          rows={4}
          onChange={(e) => setEditText(e.target.value)}
          style={{ resize: 'vertical', minHeight: '100px' }}
        />
        <div className="review-edit-actions">
          <button 
            className="btn-primary" 
            onClick={handleSave} 
            disabled={loading}
            style={{ marginRight: '8px' }}
          >
            {loading ? 'Saving...' : 'Save'}
          </button>
          <button 
            className="btn-secondary" 
            onClick={() => setEditing(false)} 
            disabled={loading}
          >
            Cancel
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="review-card">
      <div className="review-card__header">
        <div className="review-card__meta">
          <span className="review-avatar">
            {review.username.charAt(0).toUpperCase()}
          </span>
          <div>
            <span className="review-username">{review.username}</span>
            <span className="review-date">
              {formatDate(review.created_at)}
              {review.edited_at && <em style={{ color: '#888', marginLeft: '6px' }}>(edited)</em>}
            </span>
          </div>
        </div>
        <StarDisplay score={review.score} />
      </div>

      {review.review_title && (
        <h4 className="review-title-text">"{review.review_title}"</h4>
      )}
      
      <p className="review-body">{review.review_text}</p>

      {isOwner && (
        <div className="review-card__actions">
          <button 
            className="review-action-btn" 
            onClick={() => setEditing(true)}
            style={{ color: '#e2b616', marginRight: '12px' }}
          >
            ✏️ Edit
          </button>
          <button 
            className="review-action-btn" 
            onClick={handleDelete}
            style={{ color: '#e55' }}
          >
            🗑️ Delete
          </button>
        </div>
      )}
    </div>
  );
}
