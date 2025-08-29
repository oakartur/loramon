'use client'

import { useState } from 'react'
import { apiPost } from '@/lib/api'

type Row = Record<string, unknown>
type SqlResult = { rows: Row[]; columns?: string[] }

export default function SqlToolPage() {
  const [query, setQuery] = useState('select now() as now')
  const [rows, setRows] = useState<Row[]>([])
  const [err, setErr] = useState<string>('')

  async function run() {
    setErr('')
    try {
      const res = await apiPost<SqlResult>('/sql/run', { query, limit: 500 })
      setRows(res.rows ?? [])
    } catch (e: any) {
      setErr(String(e?.message ?? e))
    }
  }

  const columns =
    rows.length > 0 ? Object.keys(rows[0]) : []

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">SQL Playground</h1>

      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="w-full h-40 p-3 rounded border"
        spellCheck={false}
      />

      <button
        onClick={run}
        className="px-4 py-2 rounded bg-blue-600 text-white"
      >
        Executar
      </button>

      {err && <div className="text-red-600">{err}</div>}

      {rows.length > 0 && (
        <div className="overflow-auto border rounded">
          <table className="min-w-full text-sm">
            <thead>
              <tr>
                {columns.map((c) => (
                  <th key={c} className="text-left p-2 border-b">{c}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={i} className="odd:bg-gray-50">
                  {columns.map((c) => (
                    <td key={c} className="p-2 border-b">
                      {String((r as any)[c] ?? '')}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
