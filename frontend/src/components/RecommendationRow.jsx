import { Link } from 'react-router-dom';
import { truncate, getGenreList } from '../utils/helpers';

export default function RecommendationRow({ title, movies, loading, emptyMessage }) {
  if (loading) {
    return (
      <section className="rec-row">
        <h2 className="row-title">{title}</h2>
        <div className="row-scroll">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="rec-card skeleton">
              <div className="skeleton-poster" />
              <div className="skeleton-line short" style={{ marginTop: 8 }} />
            </div>
          ))}
        </div>
      </section>
    );
  }

  if (!movies || movies.length === 0) {
    return (
      <section className="rec-row">
        <h2 className="row-title">{title}</h2>
        <p className="row-empty">{emptyMessage || 'Nothing to show here yet.'}</p>
      </section>
    );
  }

  return (
    <section className="rec-row">
      <h2 className="row-title">{title}</h2>
      <div className="row-scroll">
        {movies.map((item) => {
          const movie = item.movie || item;
          const score = item.score;
          const method = item.method;
          const genres = getGenreList(movie.genres);
          return (
            <Link key={movie.id} to={`/movies/${movie.id}`} className="rec-card">
              <div className="rec-poster">
                <img
                  src={movie.poster_url || `https://picsum.photos/seed/${movie.id}/200/300`}
                  alt={movie.title}
                  loading="lazy"
                  onError={(e) => { e.target.src = `https://picsum.photos/seed/movie${movie.id}/200/300`; }}
                />
                {score != null && (
                  <span className="rec-score">{Math.round(score * 100)}%</span>
                )}
                {method && (
                  <span className={`rec-badge badge-${method}`}>
                    {method === 'hybrid' ? '🔮' : method === 'content' ? '🎯' : method === 'popular' ? '🔥' : '🤝'}
                  </span>
                )}
              </div>
              <div className="rec-info">
                <span className="rec-title">{truncate(movie.title, 24)}</span>
                {genres[0] && <span className="rec-genre">{genres[0]}</span>}
              </div>
            </Link>
          );
        })}
      </div>
    </section>
  );
}
