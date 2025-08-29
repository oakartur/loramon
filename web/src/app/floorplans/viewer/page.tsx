'use client'
import { useEffect, useState } from 'react'
import FloorCanvas from '@/components/FloorCanvas'

export default function Viewer() {
  const [imageUrl, setImageUrl] = useState<string>('')
  const [floorId, setFloorId] = useState<string>('')

  useEffect(() => {
    // TODO: buscar planta cadastrada via API
    setFloorId('demo')
    setImageUrl('/api/floorplans/image/<FLOORPLAN_ID>')
  }, [])

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Planta – Visualização</h1>
      {imageUrl ? (
        <FloorCanvas imageUrl={imageUrl} floorplanId={floorId} />
      ) : (
        <div>Cadastre uma planta</div>
      )}
    </div>
  )
}
