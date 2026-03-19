import { create } from 'zustand'
import type { Seat, PassengerIn } from '../types'

interface SelectedSeat {
  seat: Seat
  passenger: PassengerIn
}

interface BookingStore {
  flightId: string | null
  selectedSeats: SelectedSeat[]

  setFlight: (flightId: string) => void
  toggleSeat: (seat: Seat) => void
  updatePassenger: (seatId: string, passenger: PassengerIn) => void
  clearBooking: () => void

  // Computed helpers
  isSeatSelected: (seatId: string) => boolean
  subtotal: () => number
}

const emptyPassenger = (): PassengerIn => ({
  full_name: '',
  date_of_birth: '',
  phone_number: '',
})

export const useBookingStore = create<BookingStore>((set, get) => ({
  flightId: null,
  selectedSeats: [],

  setFlight: (flightId) => {
    // If switching flights, clear previous selection
    if (get().flightId !== flightId) {
      set({ flightId, selectedSeats: [] })
    }
  },

  toggleSeat: (seat) => {
    const { selectedSeats } = get()
    const exists = selectedSeats.find((s) => s.seat.id === seat.id)
    if (exists) {
      set({ selectedSeats: selectedSeats.filter((s) => s.seat.id !== seat.id) })
    } else {
      if (selectedSeats.length >= 9) return // max 9 seats
      set({
        selectedSeats: [...selectedSeats, { seat, passenger: emptyPassenger() }],
      })
    }
  },

  updatePassenger: (seatId, passenger) => {
    set({
      selectedSeats: get().selectedSeats.map((s) =>
        s.seat.id === seatId ? { ...s, passenger } : s
      ),
    })
  },

  clearBooking: () => set({ flightId: null, selectedSeats: [] }),

  isSeatSelected: (seatId) => get().selectedSeats.some((s) => s.seat.id === seatId),

  subtotal: () =>
    get().selectedSeats.reduce((sum, s) => sum + Number(s.seat.base_price), 0),
}))