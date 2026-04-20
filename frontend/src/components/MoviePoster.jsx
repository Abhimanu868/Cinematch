import { useState } from 'react';

export default function MoviePoster({ posterUrl, title, className = '' }) {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);

  const fallbackUrl = 'https://via.placeholder.com/300x450/111827/ffffff?text=No+Poster';
  const finalSrc = error ? fallbackUrl : (posterUrl || fallbackUrl);

  return (
    <>
      {!loaded && !error && (
        <div 
          className="skeleton skeleton-poster" 
          style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 1 }}
        ></div>
      )}
      <img
        src={finalSrc}
        alt={title}
        loading="lazy"
        className={className}
        onLoad={() => setLoaded(true)}
        onError={() => setError(true)}
        style={{ opacity: loaded || error ? 1 : 0, transition: 'opacity 0.3s ease, transform 0.3s' }}
      />
    </>
  );
}
