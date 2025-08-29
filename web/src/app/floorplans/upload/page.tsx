// web/src/app/floorplans/upload/page.tsx
'use client'
import { useState } from 'react'

export default function UploadFloorplan() {
  const [siteId, setSiteId] = useState<number>(1)
  const [name, setName] = useState('')
  const [file, setFile] = useState<File|undefined>()
  const [msg, setMsg] = useState<string|undefined>()

  async function submit() {
    if (!file) return setMsg('Selecione um PDF.')
    const fd = new FormData()
    fd.append('site_id', String(siteId))
    fd.append('name', name || file.name)
    fd.append('file', file)
    const r = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || '/api'}/floorplans/upload`, {
      method: 'POST', body: fd
    })
    if (!r.ok) return setMsg(`Falhou: ${await r.text()}`)
    const data = await r.json()
    setMsg(`OK! id=${data.id}`)
  }

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-bold">Enviar Planta (PDF)</h1>
      <div className="flex flex-col gap-2 max-w-md">
        <input type="number" className="border p-2 rounded" value={siteId}
               onChange={e=>setSiteId(Number(e.target.value))} placeholder="site_id"/>
        <input className="border p-2 rounded" value={name} onChange={e=>setName(e.target.value)} placeholder="Nome"/>
        <input type="file" accept="application/pdf" onChange={e=>setFile(e.target.files?.[0])}/>
        <button onClick={submit} className="px-4 py-2 rounded bg-black text-white">Enviar</button>
        {msg && <div>{msg}</div>}
      </div>
    </div>
  )
}
