const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "/api";

export type IobCard = {
  station_id: string;
  station_name?: string;
  last_update: string;
  parameters: Record<string, { value: number; unit: string; quality_code?: number }>;
  predictions?: Record<string, { value: number; trend: string; confidence: number }>;
  alerts?: Array<{ id: number; time: string; alert_type: string; severity: string; message: string }>;
  metadata?: any;
};

export type SensorPoint = {
  time: string;
  station_id: string;
  parameter: string;
  value: number;
  unit?: string;
  quality_code?: number;
};

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`API ${res.status} ${path}`);
  return res.json() as Promise<T>;
}

export const api = {
  iobCard: () => getJson<IobCard>(`/v1/iob/card`),
  stations: () => getJson<{ stations: Array<{ id: string; name: string }> }>(`/v1/stations`),
  sensorData: (stationId: string, parameter: string, hours: number) =>
    getJson<{ station_id: string; parameter: string; unit?: string; data: SensorPoint[] }>(
      `/v1/sensor-data/${encodeURIComponent(stationId)}?parameter=${encodeURIComponent(parameter)}&hours=${hours}`
    ),
};
