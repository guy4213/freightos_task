import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { fetchBookings, cancelBooking } from '../api/bookings'
import type { Booking } from '../types'

function formatDateTime(iso: string) {
  return new Date(iso).toLocaleString('en-GB', {
    day: 'numeric', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function BookingModal({ booking, onClose }: { booking: Booking; onClose: () => void }) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Booking {booking.id.slice(0, 8)}...</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          <div className="modal-flight">
            <span className="modal-flight-num">{booking.flight_number}</span>
            <span>{booking.origin} → {booking.destination}</span>
            <span>{formatDateTime(booking.departure_at)}</span>
          </div>

          <table className="modal-passengers-table">
            <thead>
              <tr>
                <th>Seat</th>
                <th>Passenger</th>
                <th>DOB</th>
                <th>Phone</th>
                <th>Type</th>
              </tr>
            </thead>
            <tbody>
              {booking.seats.map((bs) => (
                <tr key={bs.id}>
                  <td><strong>{bs.seat_label}</strong></td>
                  <td>{bs.passenger.full_name}</td>
                  <td>{bs.passenger.date_of_birth}</td>
                  <td>{bs.passenger.phone_number}</td>
                  <td>{bs.passenger.is_infant ? '👶 Infant' : '🧑 Adult'}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="modal-total">
            Total: <strong>${booking.total_price}</strong>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function ReservationsPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [viewBooking, setViewBooking] = useState<Booking | null>(null)

  const { data: bookings, isLoading } = useQuery({
    queryKey: ['bookings'],
    queryFn: () => fetchBookings(),
  })

  const cancelMutation = useMutation({
    mutationFn: ({ bookingId }: { bookingId: string }) =>
      cancelBooking(bookingId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['bookings'] }),
  })

  return (
    <div className="page">
      <div className="page-header">
        <button className="back-btn" onClick={() => navigate('/')}>← Back to Flights</button>
        <h1>My Reservations</h1>
        <p>All bookings made in this session</p>
      </div>

      {isLoading && (
        <div className="loading">
          <div className="spinner" />
          <span>Loading reservations...</span>
        </div>
      )}

      {bookings && bookings.length === 0 && (
        <div className="empty-state">
          <span>✈</span>
          <p>No reservations yet.</p>
          <button className="select-btn" onClick={() => navigate('/')}>Browse Flights</button>
        </div>
      )}

      {bookings && bookings.length > 0 && (
        <div className="table-wrapper">
          <table className="reservations-table">
            <thead>
              <tr>
                <th>Booking ID</th>
                <th>Booked At</th>
                <th>Flight</th>
                <th>Seats</th>
                <th>Passengers</th>
                <th>Total</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {bookings.map((b) => (
                <tr key={b.id} className={b.status === 'cancelled' ? 'row-cancelled' : ''}>
                  <td className="booking-id">{b.id.slice(0, 8)}...</td>
                  <td>{formatDateTime(b.booked_at)}</td>
                  <td>
                    <strong>{b.flight_number}</strong><br />
                    <span className="route-small">{b.origin} → {b.destination}</span>
                  </td>
                  <td>{b.seats.map((s) => s.seat_label).join(', ')}</td>
                  <td>{b.seats.length} passenger{b.seats.length > 1 ? 's' : ''}</td>
                  <td><strong>${b.total_price}</strong></td>
                  <td>
                    <span className={`status-badge status-${b.status}`}>
                      {b.status}
                    </span>
                  </td>
                  <td className="actions-cell">
                    <button
                      className="action-btn view-btn"
                      onClick={() => setViewBooking(b)}
                    >
                      View
                    </button>
                    {b.status === 'active' && (
                      <button
                        className="action-btn cancel-btn"
                        onClick={() => {
                          if (confirm('Cancel this booking?')) {
                            cancelMutation.mutate({ bookingId: b.id })
                          }
                        }}
                        disabled={cancelMutation.isPending}
                      >
                        Cancel
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {viewBooking && (
        <BookingModal booking={viewBooking} onClose={() => setViewBooking(null)} />
      )}
    </div>
  )
}