import MovieCard from './MovieCard';

export default function MovieGrid({ movies, loading, onRate, showScore = false }) {
  if (loading) {
    return (
      <div className="movie-grid">
        {Array.from({ length: 12 }).map((_, i) => (
          <div key={i} className="movie-card skeleton">
            <div className="skeleton-poster" />
            <div className="skeleton-info">
              <div className="skeleton-line" />
              <div className="skeleton-line short" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (!movies || movies.length === 0) {
    return (
      <div className="empty-state">
        <span className="empty-icon">🎬</span>
        <h3>No movies found</h3>
        <p>Try a different search or explore another genre.</p>
      </div>
    );
  }

  return (
    <div className="movie-grid">
      {movies.map((movie) => (
        <MovieCard
          key={movie.id}
          movie={movie}
          onRate={onRate}
          showScore={showScore}
          score={movie.score}
          method={movie.method}
        />
      ))}
    </div>
  );
}
