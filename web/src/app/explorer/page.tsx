import ReactEChart from '@/components/ReactEChart'
import type { EChartsOption } from 'echarts'

export default function ExplorerPage() {
  const option: EChartsOption = {
    title: { text: 'Exemplo de Série' },
    tooltip: { trigger: 'axis' },
    legend: { data: ['Temperatura'] },
    xAxis: { type: 'category', data: Array.from({ length: 20 }, (_, i) => String(i+1)) },
    yAxis: { type: 'value' },
    dataZoom: [{ type: 'inside' }, { type: 'slider' }],
    series: [{ name: 'Temperatura', type: 'line', smooth: true, data: Array.from({ length: 20 }, () => Math.random()*10+20) }]
  }

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-bold">Explorer</h1>
      <div className="bg-white p-4 rounded shadow">
        <ReactEChart option={option} style={{ height: 420 }} />
      </div>
    </div>
  )
}
