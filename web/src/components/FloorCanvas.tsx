'use client'
import { TransformWrapper, TransformComponent } from 'react-zoom-pan-pinch'
import { useEffect, useState } from 'react'
import SensorIcon from '@/components/SensorIcon'

interface SensorPoint {
  id: string
  x_rel: number
  y_rel: number
  icon: string
  display_name: string
  // (opcional) últimos valores
  value?: number | null
  time?: string | null
}

export default function FloorCanvas({
  imageUrl,
  floorplanId,
  onSelect, // (opcional) callback para abrir overlay ao clicar
}: {
  imageUrl: string
  floorplanId: string
  onSelect?: (p: SensorPoint) => void
}) {
  const [points, setPoints] = useState<SensorPoint[]>([])

  useEffect(() => {
    // TODO: fetch placements + últimos valores via API:
    // GET /api/placements/by-floor/{floorplanId}
    // GET /api/timeseries/latest/floor/{floorplanId}
    setPoints([])
  }, [floorplanId])

  return (
    <div className="w-full h-[70vh] bg-gray-200 rounded overflow-hidden">
      <TransformWrapper minScale={0.3} initialScale={0.8}>
        <TransformComponent>
          <div className="relative">
            <img
              src={imageUrl}
              alt="planta"
              className="select-none pointer-events-none"
            />
            {points.map((p) => (
              <button
                key={p.id}
                type="button"
                aria-label={p.display_name}
                className="absolute -translate-x-1/2 -translate-y-1/2 cursor-pointer"
                style={{ left: `${p.x_rel * 100}%`, top: `${p.y_rel * 100}%` }}
                onClick={() => onSelect?.(p)}
              >
                <div className="flex flex-col items-center">
                  <SensorIcon icon={p.icon} />
                  <div className="text-xs bg-white px-1 rounded mt-1 shadow whitespace-nowrap">
                    {p.display_name}
                    {p.value !== undefined && p.value !== null ? `: ${p.value}` : ''}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </TransformComponent>
      </TransformWrapper>
    </div>
  )
}
