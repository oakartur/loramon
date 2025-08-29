'use client'
import { useEffect, useRef } from 'react'
import echarts, { EChartsOption } from '@/lib/echarts'

type Props = {
  option: EChartsOption
  style?: React.CSSProperties
  className?: string
}

export default function ReactEChart({ option, style, className }: Props) {
  const ref = useRef<HTMLDivElement>(null)
  const chartRef = useRef<ReturnType<typeof echarts.init> | null>(null)

  useEffect(() => {
    if (!ref.current) return
    if (!chartRef.current) {
      chartRef.current = echarts.init(ref.current)
    }
    chartRef.current.setOption(option)

    const handle = () => chartRef.current?.resize()
    window.addEventListener('resize', handle)
    return () => {
      window.removeEventListener('resize', handle)
      chartRef.current?.dispose()
      chartRef.current = null
    }
  }, [option])

  return <div ref={ref} style={style} className={className} />
}
