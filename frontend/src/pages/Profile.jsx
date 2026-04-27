import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getMyRatings, deleteRating } from '../api/client';
import { useAuthStore } from '../store/authStore';
import toast from 'react-hot-toast';

export default function Profile() {
  const { user, isAuthenticated } = useAuthStore();
  const [ratings, setRatings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) return;
    getMyRatings()
      .then((r) => setRatings(Array.isArray(r.data) ? r.data : []))
      .catch(() => setRatings([]))
      .finally(() => setLoading(false));
  }, [isAuthenticated]);

  const handleDelete = async (ratingId) => {
    try {
      await deleteRating(ratingId);
      setRatings((prev) => prev.filter((r) => r.id !== ratingId));
      toast.success('Rating removed');
    } catch {
      toast.error('Failed to delete rating');
    }
  };

  if (!isAuthenticated) return (
    <div className="auth-required-page">
      <span className="auth-icon">👤</span>
      <h2>Sign In Required</h2>
      <Link to="/login" className="btn-primary">Sign In</Link>
    </div>
  );

  return (
    <div className="profile-page">
      <div className="profile-header">
        <div className="profile-avatar">{user?.username?.[0]?.toUpperCase()}</div>
        <div className="profile-info">
          <h1>{user?.username}</h1>
          <p>{user?.email}</p>
          <span className="profile-stat">{ratings.length} movies rated</span>
        </div>
      </div>

      <div className="profile-content">
        <h2>Your Rated Movies</h2>
        {loading ? (
          <div className="loading-spinner"><div className="spinner" /></div>
        ) : ratings.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">⭐</span>
            <h3>No ratings yet</h3>
            <p>Start rating movies to get personalized recommendations!</p>
            <Link to="/" className="btn-primary">Browse Movies</Link>
          </div>
        ) : (
          <div className="ratings-list">
            {ratings.map((r) => (
              <div key={r.id} className="rating-item">
                <Link to={`/movies/${r.movie_id}`} className="rating-poster">
                  <img
                    src={r.movie_poster_url || `https://placehold.co/60x90/1f1f3d/e2b616?text=${encodeURIComponent(r.movie_title?.charAt(0) || '?')}&font=raleway`}
                    alt={r.movie_title}
                    onError={(e) => { e.target.onerror = null; e.target.src = 'https://placehold.co/60x90/1f1f3d/e2b616?text=?&font=raleway'; }}
                  />
                </Link>
                <div className="rating-details">
                  <Link to={`/movies/${r.movie_id}`} className="rating-movie-title">
                    {r.movie_title}
                  </Link>

                  <div className="rating-stars-display">
                    {[1,2,3,4,5].map((s) => (
                      <span key={s} className={`star ${r.score >= s ? 'filled' : ''}`}>★</span>
                    ))}
                    <span className="rating-score-text">{r.score}/5</span>
                  </div>

                  {r.movie_genres && (
                    <span style={{ fontSize: '0.75rem', color: '#888' }}>
                      {r.movie_genres}
                    </span>
                  )}

                  {r.review_title && (
                    <p style={{
                      margin: '6px 0 2px',
                      color: '#e2b616',
                      fontStyle: 'italic',
                      fontSize: '0.9rem',
                    }}>
                      "{r.review_title}"
                    </p>
                  )}

                  {r.review_text ? (
                    <p style={{
                      margin: '4px 0 6px',
                      color: '#ccc',
                      fontSize: '0.85rem',
                      lineHeight: '1.5',
                      whiteSpace: 'pre-wrap',
                      maxHeight: '80px',
                      overflow: 'hidden',
                      maskImage: 'linear-gradient(to bottom, black 60%, transparent 100%)',
                      WebkitMaskImage: 'linear-gradient(to bottom, black 60%, transparent 100%)',
                    }}>
                      {r.review_text}
                    </p>
                  ) : (
                    <p style={{
                      margin: '4px 0 6px',
                      color: '#555',
                      fontSize: '0.8rem',
                      fontStyle: 'italic',
                    }}>
                      No review written —{' '}
                      <Link
                        to={`/movies/${r.movie_id}`}
                        style={{ color: '#e2b616', textDecoration: 'none' }}
                      >
                        add one
                      </Link>
                    </p>
                  )}

                  <span className="rating-date">
                    {r.created_at ? new Date(r.created_at).toLocaleDateString() : ''}
                    {r.edited_at && (
                      <em style={{ marginLeft: '6px', color: '#666' }}>(edited)</em>
                    )}
                  </span>
                </div>
                <button className="rating-delete" onClick={() => handleDelete(r.id)} title="Remove rating">✕</button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
