import { z } from "zod";

const env = z
  .object({
    VITE_API_URL: z.string().min(1),
  })
  .parse(import.meta.env);

const API_BASE = env.VITE_API_URL;

const WardSchema = z.object({
  code: z.string(),
  name: z.string(),
});

const WardsResponseSchema = z.object({
  wards: z.array(WardSchema),
});

const ObservationSchema = z.object({
  datetime: z.string(),
  temperature: z.number().optional(),
  wind_speed: z.number().optional(),
  wind_direction: z.string().optional(),
  precipitation: z.number().optional(),
});

const ObservationsResponseSchema = z.object({
  items: z.array(ObservationSchema),
});

export type Ward = z.infer<typeof WardSchema>;
export type Observation = z.infer<typeof ObservationSchema>;

export async function fetchWards(): Promise<Ward[]> {
  const res = await fetch(`${API_BASE}/wards`);
  if (!res.ok) throw new Error(`/wards failed: ${res.status}`);
  const data = await res.json();
  return WardsResponseSchema.parse(data).wards;
}

export async function fetchObservations(ward: string): Promise<Observation[]> {
  const res = await fetch(`${API_BASE}/observations?ward=${ward}`);
  if (!res.ok) throw new Error(`/observations failed: ${res.status}`);
  const data = await res.json();
  return ObservationsResponseSchema.parse(data).items;
}
