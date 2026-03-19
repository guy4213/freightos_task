import type { Booking, BookingIn } from '../types'
import { apiRequest } from './client'
export const createBooking = (payload: BookingIn) =>
  apiRequest<Booking>('/api/bookings', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const fetchBookings = () =>
  apiRequest<Booking[]>('/api/bookings')

export const cancelBooking = (bookingId: string) =>
  apiRequest<Booking>(`/api/bookings/${bookingId}/cancel`, {
    method: 'PATCH',
  })