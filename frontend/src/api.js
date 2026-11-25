// All URLs are relative: in the kiosk the backend serves this UI, and in
// development Vite proxies /api and /photos to the backend (vite.config.js).

async function call(method, path) {
  const res = await fetch(path, { method })
  const body = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(body.detail || `Request failed (${res.status})`)
  return body
}

export const getStatus = () => call('GET', '/api/camera/status')
export const takePhoto = async () => (await call('POST', '/api/camera/release')).photo
// A fresh query string makes the browser open a new stream after a reconnect.
export const liveUrl = () => `/api/camera/live?t=${Date.now()}`
export const photoUrl = (name) => `/photos/${encodeURIComponent(name)}`
