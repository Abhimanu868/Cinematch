import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { getMovies, searchMovies, getTrending, getGenres } from '../api/client';
import MovieGrid from '../components/MovieGrid';
import RecommendationRow from '../components/RecommendationRow';
import { useAuthStore } from '../store/authStore';

export default function Home() {
  const [movies, setMovies] = useState([]);
  const [trending, setTrending] = useState([]);
  const [genres, setGenres] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [trendingLoading, setTrendingLoading] = useState(true);
  const [selectedGenre, setSelectedGenre] = useState('');
  const [sortBy, setSortBy] = useState('popularity');
  const [searchParams] = useSearchParams();
  const { isAuthenticated } = useAuthStore();
  const searchQuery = searchParams.get('search') || '';

  const fetchMovies = useCallback(async () => {
    setLoading(true);
    try {
      let res;
      if (searchQuery) {
        res = await searchMovies(searchQuery);
        setMovies(res.data.movies);
        setTotal(res.data.total);
      } else {
        res = await getMovies({ page, per_page: 24, genre: selectedGenre || undefined, sort_by: sortBy });
        setMovies(res.data.movies);
        setTotal(res.data.total);
      }
    } catch (e) {
      console.error('Failed to fetch movies:', e?.response?.data || e?.message || e);
      setMovies([]);
    } finally {
      setLoading(false);
    }
  }, [searchQuery, page, selectedGenre, sortBy]);

  useEffect(() => {
    fetchMovies();
  }, [fetchMovies]);

  useEffect(() => {
    getTrending(10).then((r) => { setTrending(r.data); setTrendingLoading(false); }).catch(() => setTrendingLoading(false));
    getGenres().then((r) => setGenres(r.data)).catch(() => {});
  }, []);

  const perPage = 24;
  const totalPages = Math.ceil(total / perPage);

  return (
    <div className="page-home">
      {/* Hero */}
      {!searchQuery && (
        <section className="hero">
          <div className="hero-bg" />
          <div className="hero-content">
            <h1 className="hero-title">Discover Your Next<br /><span className="gradient-text">Favorite Movie</span></h1>
            <p className="hero-subtitle">AI-powered recommendations tailored just for you. Rate movies, get personalized picks.</p>
            {!isAuthenticated && (
              <a href="/register" className="btn-primary hero-cta">Get Started Free →</a>
            )}
          </div>
        </section>
      )}

      <div className="page-content">
        {/* Trending row */}
        {!searchQuery && (
          <RecommendationRow
            title="🔥 Trending Now"
            movies={trending.map(m => ({ movie: m }))}
            loading={trendingLoading}
          />
        )}

        {/* Filters */}
        {!searchQuery && (
          <div className="filters-bar">
            <h2 className="section-title">Browse Movies</h2>
            <div className="filters">
              <select className="filter-select" value={selectedGenre} onChange={(e) => { setSelectedGenre(e.target.value); setPage(1); }}>
                <option value="">All Genres</option>
                {genres.map((g) => <option key={g} value={g}>{g}</option>)}
              </select>
              <select className="filter-select" value={sortBy} onChange={(e) => { setSortBy(e.target.value); setPage(1); }}>
                <option value="popularity">Most Popular</option>
                <option value="rating">Highest Rated</option>
                <option value="year">Newest First</option>
                <option value="title">A–Z</option>
              </select>
            </div>
          </div>
        )}

        {searchQuery && (
          <div className="search-header">
            <h2>Results for "<span className="gradient-text">{searchQuery}</span>"</h2>
            <span className="result-count">{total} movies found</span>
          </div>
        )}

        <MovieGrid movies={movies} loading={loading} />

        {/* Pagination */}
        {!searchQuery && totalPages > 1 && (
          <div className="pagination">
            <button className="page-btn" disabled={page === 1} onClick={() => setPage(p => p - 1)}>← Prev</button>
            <span className="page-info">Page {page} of {totalPages}</span>
            <button className="page-btn" disabled={page === totalPages} onClick={() => setPage(p => p + 1)}>Next →</button>
          </div>
        )}
      </div>
    </div>
  );
}
