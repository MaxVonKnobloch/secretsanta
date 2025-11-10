// Utility function for safe JSON fetch under /secretsanta
export async function fetchJsonSafe(url, options = {}) {
  // normalize URLs: make /api/... → /secretsanta/api/...
  const normalizeUrl = (u) => {
    if (!u) return '/secretsanta/api';
    if (/^https?:\/\//i.test(u)) return u; // already absolute
    if (u.startsWith('/api/')) return '/secretsanta' + u;
    if (u.startsWith('api/')) return '/secretsanta/' + u;
    return u;
  };

  const finalUrl = normalizeUrl(url);

  const defaultOptions = {
    credentials: 'include',
    headers: {
      Accept: 'application/json',
    },
  };

  const mergedOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...(options.headers || {}),
    },
  };

  const res = await fetch(finalUrl, mergedOptions);
  const contentType = res.headers.get('content-type') || '';
  const isJson = contentType.includes('application/json');

  let parsed = null;
  if (isJson) {
    try {
      parsed = await res.json();
    } catch {
      // ignore parse error
    }
  }

  if (!res.ok) {
    if (isJson && parsed !== null) return parsed;
    throw new Error(`Network error: ${res.status}`);
  }

  if (!isJson) throw new Error('Not JSON');
  return parsed;
}
