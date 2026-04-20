import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getMovie, getSimilarMovies } from '../api/client';
import RatingStars from '../components/RatingStars';
import RecommendationRow from '../components/RecommendationRow';
import MoviePoster from '../components/MoviePoster';
import { formatRuntime, getGenreList } from '../utils/helpers';
import { useAuthStore } from '../store/authStore';

export default function MovieDetail() {
  const { id } = useParams();
  const [movie, setMovie] = useState(null);
  const [similar, setSimilar] = useState([]);
  const [loading, setLoading] = useState(true);
  const [simLoading, setSimLoading] = useState(true);
  const { isAuthenticated } = useAuthStore();

  useEffect(() => {
    setLoading(true);
    getMovie(id)
      .then((r) => setMovie(r.data))
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
  };

  if (loading) return <div className="loading-page"><div className="spinner" /></div>;
  if (!movie) return <div className="error-page"><h2>Movie not found</h2><Link to="/">← Back home</Link></div>;

  const genres = getGenreList(movie.genres);

  return (
    <div className="movie-detail-page">
      {/* Backdrop */}
      <div className="detail-backdrop" style={!movie.backdrop_url ? { background: 'linear-gradient(to bottom, #111827, #000000)' } : {}}>
        {movie.backdrop_url && (
          <img
            src={movie.backdrop_url}
            alt=""
            style={{ filter: 'brightness(0.4)' }}
          />
        )}
        <div className="backdrop-overlay" />
      </div>

      <div className="detail-content">
        <div className="detail-main">
          {/* Poster */}
          <div className="detail-poster">
            <MoviePoster posterUrl={movie.poster_url} title={movie.title} />
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
      </div>
    </div>
  );
}
