import type { Flight, Seat } from '../types'

const BASE = import.meta.env.VITE_BASE_URL;

export async function fetchFlights(): Promise<Flight[]> {
  const res = await fetch(`${BASE}/api/flights`)
  if (!res.ok) throw new Error('Failed to fetch flights')
  return res.json()
}

export async function fetchSeats(flightId: string): Promise<Seat[]> {
  const res = await fetch(`${BASE}/api/flights/${flightId}/seats`)
  if (!res.ok) throw new Error('Failed to fetch seats')
  return res.json()
}