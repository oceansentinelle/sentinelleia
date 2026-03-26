"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

const DEFAULT_STATION = "BARAG";

const PARAMS = [
  { key: "temperature", label: "Température", color: "#ef4444" },
  { key: "salinity", label: "Salinité", color: "#3b82f6" },
  { key: "ph", label: "pH", color: "#10b981" },
  { key: "dissolved_oxygen", label: "O₂ dissous", color: "#f59e0b" },
] as const;

const WINDOWS = [
  { hours: 24, label: "24h" },
  { hours: 24 * 7, label: "7j" },
  { hours: 24 * 30, label: "30j" },
] as const;

export default function Home() {
  const [stationId] = useState(DEFAULT_STATION);
  const [param, setParam] = useState<(typeof PARAMS)[number]["key"]>("temperature");
  const [hours, setHours] = useState<number>(24);

  const cardQ = useQuery({
    queryKey: ["iobCard", stationId],
    queryFn: api.iobCard,
    refetchInterval: 30000,
  });

  const seriesQ = useQuery({
    queryKey: ["sensorData", stationId, param, hours],
    queryFn: () => api.sensorData(stationId, param, hours),
  });

  const lastUpdate = cardQ.data?.last_update;
  const kpis = useMemo(() => {
    const p = cardQ.data?.parameters ?? {};
    return PARAMS.map((x) => ({
      key: x.key,
      label: x.label,
      value: p[x.key]?.value,
      unit: p[x.key]?.unit,
      qc: p[x.key]?.quality_code,
      color: x.color,
    }));
  }, [cardQ.data]);

  const chartData = (seriesQ.data?.data ?? []).map((d) => ({
    time: new Date(d.time).toLocaleString("fr-FR", {
      hour: "2-digit",
      minute: "2-digit",
      day: "2-digit",
      month: "2-digit",
    }),
    value: d.value,
  }));

  const selectedParam = PARAMS.find((p) => p.key === param);

  return (
    <main className="min-h-screen p-4 md:p-8 space-y-6 bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
            Ocean Sentinel
          </h1>
          <p className="text-sm text-slate-600 mt-1">
            Station {stationId} — Bassin d&apos;Arcachon
          </p>
        </div>
        <Badge variant="secondary" className="text-xs">
          {lastUpdate
            ? `Dernière mise à jour: ${new Date(lastUpdate).toLocaleString("fr-FR")}`
            : "Chargement…"}
        </Badge>
      </div>

      <section className="grid md:grid-cols-4 gap-4">
        {cardQ.isLoading
          ? Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-32 rounded-2xl" />
            ))
          : kpis.map((k) => (
              <Card
                key={k.key}
                className="rounded-2xl border-2 hover:shadow-lg transition-shadow cursor-pointer"
                style={{ borderColor: k.color + "20" }}
                onClick={() => setParam(k.key)}
              >
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-slate-600">
                    {k.label}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex items-end justify-between">
                    <div className="text-3xl font-bold" style={{ color: k.color }}>
                      {typeof k.value === "number" ? k.value.toFixed(2) : "—"}
                    </div>
                    <span className="text-sm text-slate-500">{k.unit ?? ""}</span>
                  </div>
                  <Badge
                    variant={k.qc === 1 ? "default" : "destructive"}
                    className="text-xs"
                  >
                    QC: {k.qc ?? "?"}
                  </Badge>
                </CardContent>
              </Card>
            ))}
      </section>

      <Card className="rounded-2xl border-2">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <CardTitle className="text-xl font-semibold">
            Historique — {selectedParam?.label}
          </CardTitle>
          <div className="flex gap-2">
            {WINDOWS.map((w) => (
              <button
                key={w.hours}
                onClick={() => setHours(w.hours)}
                className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${
                  hours === w.hours
                    ? "bg-blue-600 text-white"
                    : "bg-slate-200 text-slate-700 hover:bg-slate-300"
                }`}
              >
                {w.label}
              </button>
            ))}
          </div>
        </CardHeader>
        <CardContent className="h-[400px]">
          {seriesQ.isLoading ? (
            <Skeleton className="h-full w-full rounded-xl" />
          ) : chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis
                  dataKey="time"
                  tick={{ fontSize: 12 }}
                  stroke="#64748b"
                />
                <YAxis tick={{ fontSize: 12 }} stroke="#64748b" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "white",
                    border: "1px solid #e2e8f0",
                    borderRadius: "8px",
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke={selectedParam?.color}
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-full text-slate-500">
              Aucune donnée disponible
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="rounded-2xl border-2">
        <CardHeader>
          <CardTitle className="text-xl font-semibold">Alertes actives</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {cardQ.data?.alerts && cardQ.data.alerts.length > 0 ? (
            cardQ.data.alerts.slice(0, 5).map((a) => (
              <div
                key={a.id}
                className="p-3 rounded-xl border-2 border-orange-200 bg-orange-50"
              >
                <div className="flex items-center justify-between mb-2">
                  <Badge variant="destructive">{a.severity}</Badge>
                  <span className="text-xs text-slate-600">
                    {new Date(a.time).toLocaleString("fr-FR")}
                  </span>
                </div>
                <div className="font-medium text-sm">{a.alert_type}</div>
                <div className="text-sm text-slate-600 mt-1">{a.message}</div>
              </div>
            ))
          ) : (
            <div className="text-center py-8 text-slate-500">
              ✅ Aucune alerte active
            </div>
          )}
        </CardContent>
      </Card>
    </main>
  );
}
