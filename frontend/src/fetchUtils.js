// Utility function for safe JSON fetch
export async function fetchJsonSafe(url, options = {}) {
  const defaultOptions = {
    // include cookies for cross-origin requests (frontend <-> backend on different ports)
    credentials: 'include',
    headers: {
      'Accept': 'application/json',
    },
  };

  // Merge headers correctly (preserve any headers passed in options)
  const mergedOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...(options.headers || {}),
    },
  };

  const res = await fetch(url, mergedOptions);
  const contentType = res.headers.get('content-type') || '';
  const isJson = contentType.includes('application/json');

  // Try to parse JSON if present
  let parsed = null;
  if (isJson) {
    try {
      parsed = await res.json();
    } catch (err) {
      // fall through; parsed remains null
    }
  }

  if (!res.ok) {
    // If the server returned JSON error body, return it so callers can inspect {success:false,...}
    if (isJson && parsed !== null) return parsed;
    // Otherwise throw so callers can catch a network-like error
    throw new Error(`Network error: ${res.status}`);
  }

  if (!isJson) throw new Error('Not JSON');
  return parsed;
}
