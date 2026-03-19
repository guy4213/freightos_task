export type SeatType = 'window' | 'middle' | 'aisle'
export type SeatStatus = 'available' | 'reserved' | 'selected'
export type BookingStatus = 'active' | 'cancelled'

export interface Flight {
  id: string
  flight_number: string
  origin: string
  destination: string
  departure_at: string
  arrival_at: string
  available_seats: number
}

export interface Seat {
  id: string
  label: string
  row_number: number
  column_letter: string
  seat_type: SeatType
  base_price: number
  status: 'available' | 'reserved'
}

export interface PassengerIn {
  full_name: string
  date_of_birth: string
  phone_number: string
}

export interface SeatBookingIn {
  seat_id: string
  passenger: PassengerIn
}

export interface BookingIn {
  flight_id: string
  seats: SeatBookingIn[]
}

export interface PassengerOut {
  id: string
  full_name: string
  date_of_birth: string
  phone_number: string
  is_infant: boolean
}

export interface BookingSeatOut {
  id: string
  seat_id: string
  seat_label: string
  passenger: PassengerOut
}

export interface Booking {
  id: string
  session_id: string
  flight_id: string
  flight_number: string
  origin: string
  destination: string
  departure_at: string
  booked_at: string
  total_price: number
  status: BookingStatus
  seats: BookingSeatOut[]
}

// Frontend-only: selected seat with its form data
export interface SelectedSeat {
  seat: Seat
  passenger: PassengerIn
}