const configuredBaseUrl = (import.meta.env.VITE_API_BASE_URL || '').trim();
const API_BASE_URL = configuredBaseUrl.replace(/\/+$/, '');

/** Keep local development same-origin, while allowing Vercel to call Render in production. */
export function apiUrl(path = '') {
  if (/^https?:\/\//i.test(path)) return path;
  if (!API_BASE_URL) return path;
  return `${API_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`;
}
