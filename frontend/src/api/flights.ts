import { apiRequest } from './client'
import type { Flight, Seat } from '../types'

export const fetchFlights = () =>
  apiRequest<Flight[]>('/api/flights')

export const fetchSeats = (flightId: string) =>
  apiRequest<Seat[]>(`/api/flights/${flightId}/seats`)