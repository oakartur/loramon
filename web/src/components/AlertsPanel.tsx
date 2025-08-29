'use client'

export default function AlertsPanel() {
  // TODO: integrar com endpoint de alertas
  const alerts: { id: string; msg: string; severity: string }[] = []

  return (
    <div className="bg-white p-4 rounded shadow">
      <h2 className="font-semibold mb-2">Alertas</h2>
      {alerts.length === 0 && (
        <div className="text-gray-500 text-sm">Nenhum alerta configurado</div>
      )}
      <ul className="space-y-1">
        {alerts.map((a) => (
          <li key={a.id} className="text-sm">
            <span
              className={
                a.severity === 'critical'
                  ? 'text-red-600'
                  : a.severity === 'major'
                  ? 'text-orange-600'
                  : 'text-gray-700'
              }
            >
              {a.msg}
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}
