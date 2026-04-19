import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useAuthStore } from '../store/authStore';
import SearchBar from './SearchBar';

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuthStore();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="navbar-brand">
          <span className="brand-icon">🎬</span>
          <span className="brand-text">CineAI</span>
        </Link>

        <div className="navbar-search">
          <SearchBar />
        </div>

        <div className="navbar-links">
          <Link to="/" className="nav-link">Home</Link>
          {isAuthenticated && (
            <>
              <Link to="/recommendations" className="nav-link">For You</Link>
              <Link to="/profile" className="nav-link">Profile</Link>
            </>
          )}
        </div>

        <div className="navbar-auth">
          {isAuthenticated ? (
            <div className="user-menu">
              <button className="user-avatar" onClick={() => setMenuOpen(!menuOpen)}>
                {user?.username?.[0]?.toUpperCase() || 'U'}
              </button>
              {menuOpen && (
                <div className="dropdown">
                  <span className="dropdown-username">@{user?.username}</span>
                  <Link to="/profile" className="dropdown-item" onClick={() => setMenuOpen(false)}>Profile</Link>
                  <button className="dropdown-item danger" onClick={handleLogout}>Sign Out</button>
                </div>
              )}
            </div>
          ) : (
            <div className="auth-buttons">
              <Link to="/login" className="btn-ghost">Sign In</Link>
              <Link to="/register" className="btn-primary">Get Started</Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
