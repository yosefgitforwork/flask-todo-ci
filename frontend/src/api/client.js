// Thin fetch wrapper around the todos REST API.
//
// The base URL comes from VITE_API_URL at build time, defaulting to "/api". In
// both dev (Vite proxy) and prod (nginx proxy) that path is forwarded to the
// Flask backend on the same origin, so the browser never deals with CORS.
const BASE_URL = import.meta.env.VITE_API_URL || '/api'

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })

  // Throw on any non-2xx so callers can rely on a resolved promise = success.
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = body.message || body.error || detail
    } catch {
      /* no JSON body to read */
    }
    throw new Error(`${res.status} ${detail}`)
  }

  // 204 No Content (e.g. DELETE) has no body to parse.
  if (res.status === 204) return null
  return res.json()
}

export const todosApi = {
  list: () => request('/todos'),

  // Receives an object with title and optional priority ({ title, priority })
  create: ({ title, priority }) =>
    request('/todos', {
      method: 'POST',
      body: JSON.stringify({ title, priority }),
    }),

  toggle: (id, complete) =>
    request(`/todos/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ complete }),
    }),

  // New method for updating priority via PATCH
  updatePriority: (id, priority) =>
    request(`/todos/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ priority }),
    }),

  remove: (id) =>
    request(`/todos/${id}`, {
      method: 'DELETE',
    }),
}