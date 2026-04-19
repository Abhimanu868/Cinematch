import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { login } from '../api/client';
import { useAuthStore } from '../store/authStore';
import toast from 'react-hot-toast';

export default function Login() {
  const [form, setForm] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const { setAuth } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.username || !form.password) { toast.error('Fill in all fields'); return; }
    setLoading(true);
    try {
      const res = await login(form);
      const { access_token } = res.data;
      // Fetch user profile
      const { getMe } = await import('../api/client');
      const meRes = await getMe();
      setAuth(meRes.data, access_token);
      toast.success(`Welcome back, ${meRes.data.username}!`);
      navigate('/');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-header">
          <span className="auth-icon">🎬</span>
          <h1>Welcome Back</h1>
          <p>Sign in to get personalized movie recommendations</p>
        </div>
        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="login-username">Username</label>
            <input id="login-username" type="text" className="form-input" placeholder="Your username"
              value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
          </div>
          <div className="form-group">
            <label htmlFor="login-password">Password</label>
            <input id="login-password" type="password" className="form-input" placeholder="Your password"
              value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          </div>
          <button type="submit" className="btn-primary btn-full" disabled={loading}>
            {loading ? 'Signing in…' : 'Sign In'}
          </button>
        </form>
        <p className="auth-footer">Don't have an account? <Link to="/register">Register free</Link></p>
        <div className="demo-hint">
          <strong>Demo:</strong> username <code>user1</code> password <code>password123</code>
        </div>
      </div>
    </div>
  );
}
