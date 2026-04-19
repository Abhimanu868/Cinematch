import axios from 'axios';
import { useAuthStore } from '../store/authStore';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to every request
client.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auto-logout on 401
client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      useAuthStore.getState().logout();
    }
    return Promise.reject(err);
  }
);

// Auth
export const register = (data) => client.post('/api/auth/register', data);
export const login = (data) => client.post('/api/auth/login', data);
export const getMe = () => client.get('/api/auth/me');

// Movies
export const getMovies = (params) => client.get('/api/movies', { params });
export const searchMovies = (q) => client.get('/api/movies/search', { params: { q } });
export const getTrending = (limit = 20) => client.get('/api/movies/trending', { params: { limit } });
export const getMovie = (id) => client.get(`/api/movies/${id}`);
export const getGenres = () => client.get('/api/movies/genres');

// Ratings
export const submitRating = (data) => client.post('/api/ratings', data);
export const getMyRatings = () => client.get('/api/ratings/my-ratings');
export const deleteRating = (id) => client.delete(`/api/ratings/${id}`);

// Recommendations
export const getPersonalRecs = (top_n = 20) => client.get('/api/recommendations/personal', { params: { top_n } });
export const getSimilarMovies = (movieId, top_n = 12) => client.get(`/api/recommendations/similar/${movieId}`, { params: { top_n } });
export const getPopularRecs = (top_n = 20) => client.get('/api/recommendations/popular', { params: { top_n } });

export default client;
