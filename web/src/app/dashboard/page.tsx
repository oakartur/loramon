'use client';

import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';
import { apiGet } from '@/lib/api';

type Overview = {
  sensors_ativos: number;
  ultima_atualizacao: string; // ISO
  total_alertas_config: number;
};

type Device = { id: string; name: string };
type SeriesPoint = { ts: number; value: number };

function suggestedStep(mins: number): number {
  if (mins <= 30) return 15;
  if (mins <= 60) return 60;
  if (mins <= 6 * 60) return 300; // 5 min
  if (mins <= 24 * 60) return 900; // 15 min
  return 3600; // 1h
}

function formatDateTime(iso: string) {
  const d = new Date(iso);
  const fmt = new Intl.DateTimeFormat('pt-BR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
  const relFmt = new Intl.RelativeTimeFormat('pt-BR', { numeric: 'auto' });
  const secDiff = Math.round((Date.now() - d.getTime()) / 1000);
  const rel =
    secDiff < 60
      ? relFmt.format(-secDiff, 'second')
      : relFmt.format(-Math.round(secDiff / 60), 'minute');
  return { abs: fmt.format(d), rel };
}

export default function DashboardPage() {
  // Top cards
  const [ov, setOv] = useState<Overview | null>(null);

  // Filters
  const [minutes, setMinutes] = useState<number>(60);
  const [applications, setApplications] = useState<string[]>([]);
  const [application, setApplication] = useState<string>('');
  const [devices, setDevices] = useState<Device[]>([]);
  const [device, setDevice] = useState<string>('');
  const [metrics, setMetrics] = useState<string[]>([]);
  const [metric, setMetric] = useState<string>('');

  // Series
  const [series, setSeries] = useState<SeriesPoint[]>([]);
  const [loadingSeries, setLoadingSeries] = useState(false);

  // Auto refresh
  const [auto, setAuto] = useState(true);
  const [autoEvery, setAutoEvery] = useState(30); // seconds
  const timerRef = useRef<number | null>(null);

  const step = useMemo(() => suggestedStep(minutes), [minutes]);

  // Load applications once
  useEffect(() => {
    (async () => {
      try {
        const apps = await apiGet<{ value: string; label: string }[]>(
          '/catalog/applications',
        );
        setApplications(apps.map((a) => a.value));
      } catch {
        setApplications([]);
      }
    })();
  }, []);

  // Load overview whenever minutes changes or on tick
  const loadOverview = async () => {
    try {
      const data = await apiGet<Overview>(`/metrics/overview?minutes=${minutes}`);
      setOv(data);
    } catch {
      setOv(null);
    }
  };

  useEffect(() => {
    loadOverview();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [minutes]);

  // Auto refresh (overview + series if selected)
  useEffect(() => {
    if (!auto) {
      if (timerRef.current) window.clearInterval(timerRef.current);
      timerRef.current = null;
      return;
    }
    timerRef.current = window.setInterval(() => {
      loadOverview();
      if (device && metric) void handleApply();
    }, autoEvery * 1000) as unknown as number;

    return () => {
      if (timerRef.current) window.clearInterval(timerRef.current);
      timerRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [auto, autoEvery, device, metric, minutes, application]);

  // Load devices when application changes
  useEffect(() => {
    (async () => {
      try {
        const path = application
          ? `/catalog/devices?application=${encodeURIComponent(application)}`
          : '/catalog/devices';
        const devs = await apiGet<{ value: string; label: string }[]>(path);
        setDevices(devs.map((d) => ({ id: d.value, name: d.label })));
      } catch {
        setDevices([]);
      } finally {
        setDevice('');
        setMetrics([]);
        setMetric('');
        setSeries([]);
      }
    })();
  }, [application]);

  // Load metrics when application/device changes
  useEffect(() => {
    (async () => {
      try {
        const params = new URLSearchParams();
        if (application) params.set('application', application);
        if (device) params.set('device', device);
        const query = params.toString();
        const path = query
          ? `/catalog/metrics?${query}`
          : '/catalog/metrics';
        const mets = await apiGet<{ value: string; label: string }[]>(path);
        setMetrics(mets.map((m) => m.value));
      } catch {
        setMetrics([]);
      } finally {
        setMetric('');
        setSeries([]);
      }
    })();
  }, [application, device]);

  const handleClear = () => {
    setApplication('');
    setDevice('');
    setMetric('');
    setSeries([]);
  };

  const handleApply = async () => {
    if (!device || !metric) return;
    setLoadingSeries(true);
    try {
      const params = new URLSearchParams({
        device,
        metric,
        minutes: String(minutes),
        step: String(step),
      });
      if (application) params.set('application', application);
      const data = await apiGet<SeriesPoint[]>(`/metrics/series?${params}`);
      setSeries(data);
    } catch {
      setSeries([]);
    } finally {
      setLoadingSeries(false);
    }
  };

  // Chart data mapped for Recharts (ms timestamps)
  const chartData = useMemo(
    () =>
      series.map((p) => ({
        t: p.ts * 1000,
        value: p.value,
      })),
    [series]
  );

  const xMin = series.length ? series[0].ts * 1000 : undefined;
  const xMax = series.length ? series[series.length - 1].ts * 1000 : undefined;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-semibold">Dashboard</h1>
        <div className="flex items-center gap-3">
          <span className="text-gray-600">Auto-refresh</span>
          <button
            onClick={() => setAuto((v) => !v)}
            className={`px-3 py-1 rounded-full text-sm ${
              auto ? 'bg-green-100 text-green-700' : 'bg-gray-200 text-gray-700'
            }`}
            title="Liga/desliga o auto-refresh"
          >
            {auto ? `ON ${autoEvery}s` : 'OFF'}
          </button>
          <select
            value={autoEvery}
            onChange={(e) => setAutoEvery(Number(e.target.value))}
            className="border rounded px-2 py-1 text-sm"
            title="Intervalo de atualização automática"
          >
            {[15, 30, 60, 120].map((s) => (
              <option key={s} value={s}>
                {s}s
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Cards */}
      <div className="grid md:grid-cols-3 gap-4">
        <div className="rounded-2xl border p-5">
          <div className="text-sm text-gray-600">SENSORES ATIVOS</div>
          <div className="text-4xl font-semibold mt-2">{ov?.sensors_ativos ?? 0}</div>
        </div>

        <div className="rounded-2xl border p-5">
          <div className="text-sm text-gray-600">ÚLTIMA ATUALIZAÇÃO</div>
          <div className="text-xl font-medium mt-2">
            {ov ? formatDateTime(ov.ultima_atualizacao).abs : '--'}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {ov ? formatDateTime(ov.ultima_atualizacao).rel : ''}
          </div>
        </div>

        <div className="rounded-2xl border p-5">
          <div className="text-sm text-gray-600">ALERTAS CONFIGURADOS</div>
          <div className="text-4xl font-semibold mt-2">{ov?.total_alertas_config ?? 0}</div>
        </div>
      </div>

      {/* Filters */}
      <div className="rounded-2xl border p-5">
        <div className="grid lg:grid-cols-5 md:grid-cols-2 gap-4">
          <div className="flex flex-col gap-2">
            <label className="text-sm text-gray-600">Tempo (min)</label>
            <select
              value={minutes}
              onChange={(e) => setMinutes(Number(e.target.value))}
              className="border rounded px-3 py-2"
            >
              {[15, 30, 60, 120, 240, 480, 1440].map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
            <span className="text-xs text-gray-500">Passo sugerido: {step}s</span>
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-sm text-gray-600">Aplicação</label>
            <select
              value={application}
              onChange={(e) => setApplication(e.target.value)}
              className="border rounded px-3 py-2"
            >
              <option value="">— todas —</option>
              {applications.map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-sm text-gray-600">Dispositivo</label>
            <select
              value={device}
              onChange={(e) => setDevice(e.target.value)}
              className="border rounded px-3 py-2"
            >
              <option value="">— selecione —</option>
              {devices.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-sm text-gray-600">Métrica</label>
            <select
              value={metric}
              onChange={(e) => setMetric(e.target.value)}
              className="border rounded px-3 py-2"
            >
              <option value="">— selecione —</option>
              {metrics.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-end gap-3">
            <button
              onClick={handleApply}
              className="h-10 px-4 rounded-lg bg-black text-white hover:opacity-90 disabled:opacity-40"
              disabled={!device || !metric || loadingSeries}
            >
              {loadingSeries ? 'Carregando...' : 'Atualizar'}
            </button>
            <button
              onClick={handleClear}
              className="h-10 px-4 rounded-lg border hover:bg-gray-50"
            >
              Limpar seleção
            </button>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="rounded-2xl border p-5">
        <div className="flex items-center justify-between mb-3">
          <div className="text-lg font-medium">Série temporal</div>
          <div className="text-sm text-gray-400">
            {series.length === 0 ? 'sem dados' : `${series.length} pontos`}
          </div>
        </div>

        <div className="h-[420px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 10 }}>
              <CartesianGrid strokeDasharray="4 4" />
              <XAxis
                dataKey="t"
                type="number"
                scale="time"
                domain={series.length ? [xMin!, xMax!] : ['auto', 'auto']}
                tickFormatter={(v: number) =>
                  new Date(v).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
                }
              />
              <YAxis allowDecimals />
              <Tooltip
                labelFormatter={(value) =>
                  new Date(Number(value)).toLocaleString('pt-BR', {
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                    day: '2-digit',
                    month: '2-digit',
                  })
                }
                formatter={(v: number) => [v, metric || 'valor']}
              />
              <Line
                type="monotone"
                dataKey="value"
                dot={false}
                strokeWidth={2}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {(!device || !metric) && (
          <p className="text-center text-gray-500 mt-6">
            Selecione uma <b>aplicação</b> (opcional), um <b>dispositivo</b> e uma <b>métrica</b>{' '}
            para ver o gráfico.
          </p>
        )}
      </div>
    </div>
  );
}
