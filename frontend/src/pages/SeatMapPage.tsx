import { useQuery } from '@tanstack/react-query'
import { useNavigate, useParams } from 'react-router-dom'
import { fetchSeats, fetchFlights } from '../api/flights'
import { useBookingStore } from '../store/bookingStore'
import type { Seat } from '../types'
import { useEffect } from 'react'

const SEAT_TYPE_LABELS: Record<string, string> = {
  window: 'Window',
  middle: 'Middle',
  aisle: 'Aisle',
}

function SeatButton({ seat }: { seat: Seat }) {
  const { toggleSeat, isSeatSelected } = useBookingStore()
  const selected = isSeatSelected(seat.id)
  const reserved = seat.status === 'reserved'

  let className = 'seat'
  if (reserved) className += ' seat-reserved'
  else if (selected) className += ' seat-selected'
  else className += ' seat-available'

  return (
    <div className="seat-wrapper">
    <button
    className={className}
    disabled={reserved}
    onClick={() => !reserved && toggleSeat(seat)}
    data-type={seat.seat_type}
    title={`${seat.label} · ${SEAT_TYPE_LABELS[seat.seat_type]} · $${seat.base_price}`}
    >
    {seat.label}
    </button>
      <div className="seat-tooltip">
        <strong>{seat.label}</strong>
        <span>{SEAT_TYPE_LABELS[seat.seat_type]}</span>
        <span>${seat.base_price}</span>
        <span className={`tooltip-status ${seat.status}`}>{reserved ? 'Reserved' : selected ? 'Selected' : 'Available'}</span>
      </div>
    </div>
  )
}

function BookingSummary({ flightId }: { flightId: string }) {
  const navigate = useNavigate()
  const { selectedSeats, subtotal } = useBookingStore()

  const { data: flights } = useQuery({ queryKey: ['flights'], queryFn: fetchFlights })
  const flight = flights?.find((f) => f.id === flightId)

  return (
    <div className="booking-summary">
      <h3>Your Selection</h3>

      {flight && (
        <div className="summary-flight">
          <span className="summary-flight-num">{flight.flight_number}</span>
          <span>{flight.origin} → {flight.destination}</span>
        </div>
      )}

      <div className="summary-seats">
        {selectedSeats.length === 0 ? (
          <p className="no-seats">No seats selected yet</p>
        ) : (
          selectedSeats.map((s) => (
            <div key={s.seat.id} className="summary-seat-row">
              <span className="summary-seat-label">{s.seat.label}</span>
              <span className="summary-seat-type">{SEAT_TYPE_LABELS[s.seat.seat_type]}</span>
              <span className="summary-seat-price">${s.seat.base_price}</span>
            </div>
          ))
        )}
      </div>

      <div className="summary-total">
        <span>Subtotal</span>
        <span>${subtotal()}</span>
      </div>

      <div className="summary-count">
        {selectedSeats.length} / 9 seats selected
      </div>

      <button
        className="continue-btn"
        disabled={selectedSeats.length === 0}
        onClick={() => navigate('/checkout')}
      >
        Continue to Checkout →
      </button>
    </div>
  )
}

export default function SeatMapPage() {
  const { flightId } = useParams<{ flightId: string }>()
  const navigate = useNavigate()
  const setFlight = useBookingStore((s) => s.setFlight)

 useEffect(() => {
    if (flightId) setFlight(flightId)
  }, [flightId, setFlight])  

  const { data: seats, isLoading } = useQuery({
    queryKey: ['seats', flightId],
    queryFn: () => fetchSeats(flightId!),
    enabled: !!flightId,
  })

  // Group seats by row
  const rows: Record<number, Seat[]> = {}
  if (seats) {
    for (const seat of seats) {
      if (!rows[seat.row_number]) rows[seat.row_number] = []
      rows[seat.row_number].push(seat)
    }
  }

  return (
    <div className="page seat-map-page">
      <div className="seat-map-layout">
        <div className="seat-map-main">
          <div className="page-header">
            <button className="back-btn" onClick={() => navigate('/')}>← Back</button>
            <h1>Select Your Seats</h1>
            <p>Click a seat to select it. Hover for details.</p>
          </div>

          {isLoading && (
            <div className="loading">
              <div className="spinner" />
              <span>Loading seat map...</span>
            </div>
          )}

          {seats && (
            <div className="seat-map-container">
              {/* Column headers */}
            <div className="seat-row">
            <span className="row-label" />
            {['A', 'B', 'C'].map((col) => (
                <span key={col} className="col-header">{col}</span>
            ))}
            <span className="aisle-gap" />
            {['D', 'E', 'F'].map((col) => (
                <span key={col} className="col-header">{col}</span>
            ))}
            </div>

              {Object.entries(rows).map(([rowNum, rowSeats]) => {
                const sorted = rowSeats.sort((a, b) =>
                  'ABCDEF'.indexOf(a.column_letter) - 'ABCDEF'.indexOf(b.column_letter)
                )
                return (
                  <div key={rowNum} className="seat-row">
                    <span className="row-label">{rowNum}</span>
                    {sorted.map((seat, i) => (
                      <>
                        <SeatButton key={seat.id} seat={seat} />
                        {i === 2 && <span key="gap" className="aisle-gap" />}
                      </>
                    ))}
                  </div>
                )
              })}

              {/* Legend */}
                    <div className="seat-legend">
            <div className="legend-item">
                <span className="seat seat-available legend-dot" data-type="window" />
                Window — $200
            </div>
            <div className="legend-item">
                <span className="seat seat-available legend-dot" data-type="middle" />
                Middle — $150
            </div>
            <div className="legend-item">
                <span className="seat seat-available legend-dot" data-type="aisle" />
                Aisle — $100
            </div>
            <div className="legend-item">
                <span className="seat seat-selected legend-dot" />
                Selected
            </div>
            <div className="legend-item">
                <span className="seat seat-reserved legend-dot" />
                Reserved
            </div>
            </div>
            </div>
          )}
        </div>

        <div className="seat-map-sidebar">
          {flightId && <BookingSummary flightId={flightId} />}
        </div>
      </div>
    </div>
  )
}