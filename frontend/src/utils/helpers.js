export const formatRuntime = (minutes) => {
  if (!minutes) return 'N/A';
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return h > 0 ? `${h}h ${m}m` : `${m}m`;
};

export const formatScore = (score) => {
  if (score == null) return '0%';
  return `${Math.round(score * 100)}%`;
};

export const getGenreList = (genreStr) => {
  if (!genreStr) return [];
  return genreStr.split(',').map((g) => g.trim()).filter(Boolean);
};

export const truncate = (str, len = 150) => {
  if (!str) return '';
  return str.length > len ? str.slice(0, len).trimEnd() + '…' : str;
};
