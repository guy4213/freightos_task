import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { fetchFlights } from '../api/flights'
import { useBookingStore } from '../store/bookingStore'
import type { Flight } from '../types'

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-GB', {
    day: 'numeric', month: 'short', year: 'numeric',
  })
}

function formatTime(iso: string) {
  return new Date(iso).toLocaleTimeString('en-GB', {
    hour: '2-digit', minute: '2-digit',
  })
}

function FlightCard({ flight }: { flight: Flight }) {
  const navigate = useNavigate()
  const setFlight = useBookingStore((s) => s.setFlight)

  const handleSelect = () => {
    setFlight(flight.id)
    navigate(`/flights/${flight.id}/seats`)
  }

  const duration = Math.round(
    (new Date(flight.arrival_at).getTime() - new Date(flight.departure_at).getTime()) / 60000
  )
  const hours = Math.floor(duration / 60)
  const mins = duration % 60

  return (
    <div className="flight-card" onClick={handleSelect}>
      <div className="flight-card-header">
        <span className="flight-number">{flight.flight_number}</span>
        <span className="flight-date">{formatDate(flight.departure_at)}</span>
      </div>

      <div className="flight-route">
        <div className="airport">
          <span className="airport-code">{flight.origin}</span>
          <span className="airport-time">{formatTime(flight.departure_at)}</span>
        </div>

        <div className="flight-line">
          <div className="line" />
          <span className="duration">{hours}h {mins}m</span>
          <div className="line" />
          <span className="plane">✈</span>
        </div>

        <div className="airport">
          <span className="airport-code">{flight.destination}</span>
          <span className="airport-time">{formatTime(flight.arrival_at)}</span>
        </div>
      </div>

      <div className="flight-card-footer">
        <span className={`seats-badge ${flight.available_seats < 10 ? 'low' : ''}`}>
          {flight.available_seats} seats left
        </span>
        <span className="price-range">From $100</span>
        <button className="select-btn">Select →</button>
      </div>
    </div>
  )
}

export default function FlightsPage() {
  const { data: flights, isLoading, error } = useQuery({
    queryKey: ['flights'],
    queryFn: fetchFlights,
  })

  return (
    <div className="page">
      <div className="page-header">
        <div className="logo">✈ FREIGHTOS</div>
        <h1>Available Flights</h1>
        <p>Select a flight to view the seat map</p>
      </div>

      {isLoading && (
        <div className="loading">
          <div className="spinner" />
          <span>Loading flights...</span>
        </div>
      )}

      {error && (
        <div className="error-banner">
          Failed to load flights. Is the backend running?
        </div>
      )}

      {flights && (
        <div className="flights-grid">
          {flights.map((flight) => (
            <FlightCard key={flight.id} flight={flight} />
          ))}
        </div>
      )}
    </div>
  )
}