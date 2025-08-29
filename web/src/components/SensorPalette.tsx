'use client'

const icons = [
  { key: 'thermometer', label: 'Temperatura' },
  { key: 'water_drop', label: 'Água' },
  { key: 'humidity', label: 'Umidade' },
  { key: 'power', label: 'Energia' },
]

export default function SensorPalette() {
  return (
    <div className="bg-white p-3 rounded shadow space-y-2">
      <div className="font-semibold">Sensores</div>
      <ul className="text-sm space-y-1">
        {icons.map((i) => (
          <li key={i.key} className="flex items-center gap-2">
            <span aria-hidden>•</span>
            <span>{i.label}</span>
          </li>
        ))}
      </ul>
      <div className="text-xs text-gray-500">Arraste para a planta (TODO)</div>
    </div>
  )
}
