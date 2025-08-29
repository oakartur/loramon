'use client'
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || '/api'

function getToken(): string | null {
  return typeof window !== 'undefined' ? localStorage.getItem('token') : null
}

function redirectToLogin() {
  if (typeof window !== 'undefined') {
    window.location.href = '/login'
  }
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
  const token = getToken()
  const r = await fetch(`${API_BASE}${path}`, {
    ...init,
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    cache: 'no-store',
  })
  return handle(r, 'GET', path)
}

export async function apiPost<T>(path: string, body: unknown, init?: RequestInit): Promise<T> {
  const token = getToken()
  const r = await fetch(`${API_BASE}${path}`, {
    ...init,
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(body),
  })
  return handle(r, 'POST', path)
}

// helper específico p/ login esperado pelo backend FastAPI
export async function login(username: string, password: string): Promise<{ access_token: string, token_type?: string }> {
  return apiPost('/auth/login', { username, password })
}
