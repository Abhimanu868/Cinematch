import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getPersonalRecs, getPopularRecs } from '../api/client';
import { useAuthStore } from '../store/authStore';
import MovieGrid from '../components/MovieGrid';

export default function Recommendations() {
  const { isAuthenticated } = useAuthStore();
  const [personal, setPersonal] = useState([]);
  const [popular, setPopular] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('personal');

  useEffect(() => {
    if (isAuthenticated) {
      getPersonalRecs(20)
        .then((r) => setPersonal(r.data))
        .catch(() => setPersonal([]))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
    getPopularRecs(20).then((r) => setPopular(r.data)).catch(() => setPopular([]));
  }, [isAuthenticated]);

  if (!isAuthenticated) {
    return (
      <div className="auth-required-page">
        <span className="auth-icon">🔮</span>
        <h2>Personalized Recommendations</h2>
        <p>Sign in and rate at least 5 movies to unlock AI-powered picks tailored just for you.</p>
        <Link to="/login" className="btn-primary">Sign In</Link>
      </div>
    );
  }

  const currentMovies = (tab === 'personal' ? personal : popular).map((item) => ({
    ...item.movie,
    score: item.score,
    method: item.method,
  }));

  return (
    <div className="recs-page">
      <div className="recs-header">
        <h1>🔮 Your Recommendations</h1>
        <p>Powered by AI — based on your ratings and viewing preferences</p>
      </div>

      <div className="tab-bar">
        <button className={`tab-btn ${tab === 'personal' ? 'active' : ''}`} onClick={() => setTab('personal')}>
          ✨ For You
        </button>
        <button className={`tab-btn ${tab === 'popular' ? 'active' : ''}`} onClick={() => setTab('popular')}>
          🔥 Popular
        </button>
      </div>

      <div className="recs-legend">
        <span className="legend-item"><span className="badge-hybrid">🔮</span> Hybrid AI</span>
        <span className="legend-item"><span className="badge-content">🎯</span> Content Match</span>
        <span className="legend-item"><span className="badge-popular">🔥</span> Trending</span>
      </div>

      <MovieGrid movies={currentMovies} loading={loading} showScore={true} />
    </div>
  );
}
