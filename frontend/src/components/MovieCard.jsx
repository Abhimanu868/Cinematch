import { Link } from 'react-router-dom';
import { getGenreList, truncate } from '../utils/helpers';
import RatingStars from './RatingStars';

export default function MovieCard({ movie, onRate, showScore, score, method }) {
  const genres = getGenreList(movie.genres);

  return (
    <div className="movie-card">
      <Link to={`/movies/${movie.id}`} className="card-poster-link">
        <div className="card-poster">
          <img
            src={movie.poster_url || `https://picsum.photos/seed/${movie.id}/300/450`}
            alt={movie.title}
            loading="lazy"
            onError={(e) => { e.target.src = `https://picsum.photos/seed/movie${movie.id}/300/450`; }}
          />
          <div className="card-overlay">
            <span className="card-rating">⭐ {movie.vote_average?.toFixed(1)}</span>
            {showScore && score != null && (
              <span className="card-match">{Math.round(score * 100)}% match</span>
            )}
          </div>
          {method && (
            <span className={`card-badge badge-${method}`}>
              {method === 'hybrid' ? '🔮 AI Pick' : method === 'content' ? '🎯 Similar' : method === 'popular' ? '🔥 Trending' : '🤝 Collab'}
            </span>
          )}
        </div>
      </Link>
      <div className="card-info">
        <Link to={`/movies/${movie.id}`} className="card-title">{movie.title}</Link>
        <div className="card-meta">
          {movie.release_year && <span className="card-year">{movie.release_year}</span>}
          {genres.length > 0 && <span className="card-genre">{genres[0]}</span>}
        </div>
        {movie.overview && <p className="card-overview">{truncate(movie.overview, 80)}</p>}
        {onRate && (
          <div className="card-rate">
            <RatingStars
              movieId={movie.id}
              currentRating={movie.user_rating}
              onRate={onRate}
              size="sm"
            />
          </div>
        )}
      </div>
    </div>
  );
}
