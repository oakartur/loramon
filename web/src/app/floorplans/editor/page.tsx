'use client'
import SensorPalette from '@/components/SensorPalette'

export default function Editor() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Planta – Editor</h1>
      <div className="grid grid-cols-4 gap-4">
        <div className="col-span-3 bg-white p-4 rounded shadow h-[70vh] flex items-center justify-center text-gray-400">
          (arraste sensores para cá – TODO)
        </div>
        <SensorPalette />
      </div>
    </div>
  )
}
