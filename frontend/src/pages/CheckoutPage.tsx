import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useBookingStore } from '../store/bookingStore'
import { createBooking } from '../api/bookings'
import { getSessionId } from '../utils/session'
import type { PassengerIn } from '../types'

function calculateAge(dob: string): number {
  const today = new Date()
  const birth = new Date(dob)
  let age = today.getFullYear() - birth.getFullYear()
  const m = today.getMonth() - birth.getMonth()
  if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age--
  return age
}

interface PassengerFormProps {
  seatLabel: string
  seatType: string
  seatPrice: number
  value: PassengerIn
  onChange: (p: PassengerIn) => void
  errors: Partial<Record<keyof PassengerIn, string>>
}

function PassengerForm({ seatLabel, seatType, seatPrice, value, onChange, errors }: PassengerFormProps) {
  const isInfant = value.date_of_birth ? calculateAge(value.date_of_birth) < 4 : false

  return (
    <div className="passenger-form">
      <div className="passenger-form-header">
        <span className="passenger-seat-label">{seatLabel}</span>
        <span className="passenger-seat-type">{seatType}</span>
        <span className="passenger-seat-price">${seatPrice}</span>
        {isInfant && <span className="infant-badge">Infant</span>}
      </div>

      <div className="form-row">
        <div className="form-field">
          <label>Full Name *</label>
          <input
            type="text"
            placeholder="John Doe"
            value={value.full_name}
            onChange={(e) => onChange({ ...value, full_name: e.target.value })}
            className={errors.full_name ? 'input-error' : ''}
          />
          {errors.full_name && <span className="field-error">{errors.full_name}</span>}
        </div>

        <div className="form-field">
          <label>Date of Birth *</label>
          <input
            type="date"
            value={value.date_of_birth}
            max={new Date().toISOString().split('T')[0]}
            onChange={(e) => onChange({ ...value, date_of_birth: e.target.value })}
            className={errors.date_of_birth ? 'input-error' : ''}
          />
          {errors.date_of_birth && <span className="field-error">{errors.date_of_birth}</span>}
        </div>

        <div className="form-field">
          <label>Phone Number *</label>
          <input
            type="tel"
            placeholder="+972501234567"
            value={value.phone_number}
            onChange={(e) => onChange({ ...value, phone_number: e.target.value })}
            className={errors.phone_number ? 'input-error' : ''}
          />
          {errors.phone_number && <span className="field-error">{errors.phone_number}</span>}
        </div>
      </div>
    </div>
  )
}

const SEAT_TYPE_LABELS: Record<string, string> = {
  window: 'Window', middle: 'Middle', aisle: 'Aisle',
}

export default function CheckoutPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { flightId, selectedSeats, updatePassenger, clearBooking, subtotal } = useBookingStore()
  const [fieldErrors, setFieldErrors] = useState<Record<string, Partial<Record<keyof PassengerIn, string>>>>({})
  const [globalError, setGlobalError] = useState('')
  const [submitted, setSubmitted] = useState(false)

  const mutation = useMutation({
    mutationFn: createBooking,
    onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['bookings'] })
    setSubmitted(true)
    clearBooking()
    navigate('/reservations')
    },
    onError: (err: Error) => {
      setGlobalError(err.message)
    },
  })

 if (!submitted && (!flightId || selectedSeats.length === 0)) {
    navigate('/')
    return null
  }

function validate(): boolean {
  const errors: Record<string, Partial<Record<keyof PassengerIn, string>>> = {}
  let valid = true

  const names: string[] = []
  const phones: string[] = []

  for (const { seat, passenger } of selectedSeats) {
    const e: Partial<Record<keyof PassengerIn, string>> = {}

    // ── Name ──
    const trimmedName = passenger.full_name.trim()
    if (!trimmedName) {
      e.full_name = 'Required'
      valid = false
    } else if (trimmedName.split(/\s+/).filter(w => w.length >= 2).length < 2) {
      e.full_name = 'Please enter first and last name (at least 2 characters each)'
      valid = false
    } else if (names.includes(trimmedName.toLowerCase())) {
      e.full_name = `Duplicate name "${passenger.full_name}" — each passenger must have a unique name`
      valid = false
    } else {
      names.push(trimmedName.toLowerCase())
    }

    // ── DOB ──
    if (!passenger.date_of_birth) {
      e.date_of_birth = 'Required'
      valid = false
    } else {
      const dob = new Date(passenger.date_of_birth)
      const today = new Date()
      if (dob >= today) {
        e.date_of_birth = 'Must be in the past'
        valid = false
      } else {
        const age = calculateAge(passenger.date_of_birth)
        if (age > 120) {
          e.date_of_birth = 'Age cannot exceed 120 years'
          valid = false
        }
      }
    }

    // ── Phone ──
    const trimmedPhone = passenger.phone_number.trim()
    if (!trimmedPhone) {
      e.phone_number = 'Required'
      valid = false
    } else {
      const digits = trimmedPhone.replace(/[\s\-+]/g, '')
      if (!/^\d+$/.test(digits)) {
        e.phone_number = 'Only digits, +, - and spaces allowed'
        valid = false
      } else if (digits.length < 7 || digits.length > 15) {
        e.phone_number = 'Phone must be 7–15 digits'
        valid = false
      } else if (phones.includes(trimmedPhone)) {
        e.phone_number = `Duplicate phone "${passenger.phone_number}" — each passenger must have a unique phone number`
        valid = false
      } else {
        phones.push(trimmedPhone)
      }
    }

    if (Object.keys(e).length > 0) errors[seat.id] = e
  }

  // ── Infant/Adult ratio ──
  const infants = selectedSeats.filter(({ passenger }) =>
    passenger.date_of_birth && calculateAge(passenger.date_of_birth) < 2
  ).length
  const adults = selectedSeats.length - infants

  if (infants > 0 && adults === 0) {
    setGlobalError('An infant cannot travel alone — at least one adult is required.')
    valid = false
  } else if (infants > adults) {
    setGlobalError(
      `Too many infants (${infants}) — maximum 1 infant per adult. You have ${adults} adult(s).`
    )
    valid = false
  }

  setFieldErrors(errors)
  return valid
}

  function handleSubmit() {
    setGlobalError('')
    if (!validate()) return

    mutation.mutate({
      session_id: getSessionId(),
      flight_id: flightId!,
      seats: selectedSeats.map(({ seat, passenger }) => ({
        seat_id: seat.id,
        passenger,
      })),
    })
  }

  return (
    <div className="page">
      <div className="page-header">
        <button className="back-btn" onClick={() => navigate(-1)}>← Back to Seat Map</button>
        <h1>Passenger Details</h1>
        <p>Fill in the details for each passenger</p>
      </div>

      <div className="checkout-layout">
        <div className="checkout-forms">
          {selectedSeats.map(({ seat, passenger }) => (
            <PassengerForm
              key={seat.id}
              seatLabel={seat.label}
              seatType={SEAT_TYPE_LABELS[seat.seat_type]}
              seatPrice={Number(seat.base_price)}
              value={passenger}
              onChange={(p) => updatePassenger(seat.id, p)}
              errors={fieldErrors[seat.id] || {}}
            />
          ))}
        </div>

        <div className="checkout-summary">
          <h3>Booking Summary</h3>
          {selectedSeats.map(({ seat }) => (
            <div key={seat.id} className="summary-seat-row">
              <span>{seat.label}</span>
              <span>${seat.base_price}</span>
            </div>
          ))}
          <div className="summary-total">
            <span>Total</span>
            <span>${subtotal()}</span>
          </div>

            {globalError && (
        <div className="error-popup">
            <div className="error-popup-icon">⚠️</div>
            <div className="error-popup-content">
            <strong>Cannot confirm booking</strong>
            <span>{globalError}</span>
            </div>
            <button className="error-popup-close" onClick={() => setGlobalError('')}>✕</button>
        </div>
        )}

          <button
            className="confirm-btn"
            onClick={handleSubmit}
            disabled={mutation.isPending}
          >
            {mutation.isPending ? 'Confirming...' : 'Confirm Booking ✓'}
          </button>
        </div>
      </div>
    </div>
  )
}