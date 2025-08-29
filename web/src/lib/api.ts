'use client'
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || '/api'

function authHeaders(init?: RequestInit) {
  const headers = new Headers(init?.headers)
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token')
    if (token) headers.set('Authorization', `Bearer ${token}`)
  }
  return headers

}

async function handle(r: Response, method: string, path: string) {
  if (!r.ok) {
    if (r.status === 401) {
      redirectToLogin()
    }
    const text = await r.text().catch(() => '')
    throw new Error(`${method} ${path} -> ${r.status}: ${text}`)
  }
  return r.json()
}

export async function apiGet<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = authHeaders(init)
  headers.set('Content-Type', 'application/json')
  const r = await fetch(`${API_BASE}${path}`, {
    ...init,
    method: 'GET',
    headers,

    cache: 'no-store',
  })
  return handle(r, 'GET', path)
}

export async function apiPost<T>(path: string, body: unknown, init?: RequestInit): Promise<T> {
  const headers = authHeaders(init)
  headers.set('Content-Type', 'application/json')
  const r = await fetch(`${API_BASE}${path}`, {
    ...init,
    method: 'POST',
    headers,

    body: JSON.stringify(body),
  })
  return handle(r, 'POST', path)
}

export async function apiPostForm<T>(path: string, form: FormData, init?: RequestInit): Promise<T> {
  const headers = authHeaders(init)
  const r = await fetch(`${API_BASE}${path}`, {
    ...init,
    method: 'POST',
    headers,
    body: form,
  })
  return handle(r, 'POST', path)
}

// helper específico p/ login esperado pelo backend FastAPI
export async function login(username: string, password: string): Promise<{ access_token: string, token_type?: string }> {
  return apiPost('/auth/login', { username, password })
}
