import type { Booking, BookingIn } from '../types'

const BASE = import.meta.env.VITE_BASE_URL;

export async function createBooking(payload: BookingIn): Promise<Booking> {
  const res = await fetch(`${BASE}/api/bookings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const err = await res.json()
    // detail can be a string or an object {type, message}
    const detail = err.detail
    if (typeof detail === 'object' && detail.message) {
      throw new Error(detail.message)
    }
    throw new Error(typeof detail === 'string' ? detail : 'Booking failed')
  }
  return res.json()
}

export async function fetchBookings(sessionId: string): Promise<Booking[]> {
  const res = await fetch(`${BASE}/api/bookings?session_id=${sessionId}`)
  if (!res.ok) throw new Error('Failed to fetch bookings')
  return res.json()
}

export async function cancelBooking(bookingId: string, sessionId: string): Promise<Booking> {
  const res = await fetch(`${BASE}/api/bookings/${bookingId}/cancel?session_id=${sessionId}`, {
    method: 'PATCH',
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Cancel failed')
  }
  return res.json()
}