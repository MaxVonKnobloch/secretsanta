// Utility function for safe JSON fetch
export async function fetchJsonSafe(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error('Network error');
  const contentType = res.headers.get('content-type');
  if (!contentType || !contentType.includes('application/json')) throw new Error('Not JSON');
  return res.json();
}

