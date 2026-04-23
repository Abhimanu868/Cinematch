import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getMovie, getSimilarMovies } from '../api/client';
import RatingStars from '../components/RatingStars';
import RecommendationRow from '../components/RecommendationRow';
import { formatRuntime, getGenreList } from '../utils/helpers';
import { useAuthStore } from '../store/authStore';
import WriteReview from '../components/WriteReview';
import ReviewsList from '../components/ReviewsList';

export default function MovieDetail() {
  const { id } = useParams();
  const [movie, setMovie] = useState(null);
  const [similar, setSimilar] = useState([]);
  const [loading, setLoading] = useState(true);
  const [simLoading, setSimLoading] = useState(true);
  const { isAuthenticated } = useAuthStore();
  const [reviewRefresh, setReviewRefresh] = useState(0);
  const [userRating, setUserRating] = useState(null);

  useEffect(() => {
    setLoading(true);
    getMovie(id)
      .then((r) => {
        setMovie(r.data);
        if (r.data.user_rating) {
            setUserRating({ score: r.data.user_rating });
        }
      })
      .catch(() => setMovie(null))
      .finally(() => setLoading(false));

    setSimLoading(true);
    getSimilarMovies(id)
      .then((r) => setSimilar(r.data))
      .catch(() => setSimilar([]))
      .finally(() => setSimLoading(false));
  }, [id]);

  const handleRate = (movieId, score) => {
    setMovie((m) => m ? { ...m, user_rating: score } : m);
    setUserRating((prev) => ({ ...prev, score }));
    setReviewRefresh(r => r + 1);
  };

  if (loading) return <div className="loading-page"><div className="spinner" /></div>;
  if (!movie) return <div className="error-page"><h2>Movie not found</h2><Link to="/">← Back home</Link></div>;

  const genres = getGenreList(movie.genres);
  const FALLBACK_IMAGE = "https://placehold.co/300x450/1a1a2e/white?text=No+Poster";
  const backdropStyle = movie.backdrop_url
    ? { backgroundImage: `url(${movie.backdrop_url})`, backgroundSize: 'cover', backgroundPosition: 'center' }
    : { background: "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)" };

  return (
    <div className="movie-detail-page">
      {/* Backdrop */}
      <div className="detail-backdrop" style={backdropStyle}>
        <div className="backdrop-overlay" />
      </div>

      <div className="detail-content">
        <div className="detail-main">
          {/* Poster */}
          <div className="detail-poster">
            <img
              src={movie.poster_url || FALLBACK_IMAGE}
              alt={movie.title}
              onError={(e) => { e.target.onerror = null; e.target.src = FALLBACK_IMAGE; }}
              style={{ width: "300px", borderRadius: "8px", boxShadow: "0 4px 20px rgba(0,0,0,0.5)" }}
            />
          </div>

          {/* Info */}
          <div className="detail-info">
            <div className="detail-genres">
              {genres.map((g) => <span key={g} className="genre-pill">{g}</span>)}
            </div>
            <h1 className="detail-title">{movie.title}</h1>
            {movie.tagline && <p className="detail-tagline" style={{ fontStyle: 'italic', opacity: 0.8, marginTop: '-5px', marginBottom: '15px', fontSize: '1.1rem' }}>"{movie.tagline}"</p>}
            <div className="detail-meta">
              {movie.release_year && <span>📅 {movie.release_year}</span>}
              {movie.runtime && <span>⏱ {formatRuntime(movie.runtime)}</span>}
              <span>⭐ {movie.vote_average?.toFixed(1)} ({movie.vote_count?.toLocaleString()} votes)</span>
            </div>
            {movie.director && <p className="detail-director">🎬 Directed by <strong>{movie.director}</strong></p>}
            {movie.cast && <p className="detail-cast">🎭 {movie.cast}</p>}
            {movie.overview && <p className="detail-overview">{movie.overview}</p>}

            <div className="detail-rating-section">
              {isAuthenticated ? (
                <>
                  <h3>Your Rating</h3>
                  <RatingStars movieId={movie.id} currentRating={movie.user_rating} onRate={handleRate} size="lg" />
                </>
              ) : (
                <p className="sign-in-prompt"><Link to="/login">Sign in</Link> to rate this movie</p>
              )}
            </div>
          </div>
        </div>

        {/* Similar movies */}
        <RecommendationRow
          title="🎯 Similar Movies"
          movies={similar}
          loading={simLoading}
          emptyMessage="No similar movies found yet."
        />

        {/* ── Reviews Section ── */}
        <div className="reviews-section" style={{ marginTop: '48px' }}>
          <h2 className="section-title" style={{ marginBottom: '24px' }}>
            ⭐ Ratings & Reviews
          </h2>
          
          {/* Write Review Form */}
          <WriteReview
            movieId={movie.id}
            existingRating={userRating}
            onSubmit={(newRating) => {
              setUserRating(newRating);
              setReviewRefresh(r => r + 1);
            }}
          />

          <div style={{ height: '1px', background: '#2a2a3e', margin: '32px 0' }} />

          {/* Reviews List */}
          <ReviewsList 
            movieId={movie.id} 
            refreshTrigger={reviewRefresh}
          />
        </div>
      </div>
    </div>
  );
}
