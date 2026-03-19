import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import FlightsPage from './pages/FlightsPage'
import SeatMapPage from './pages/SeatMapPage'
import CheckoutPage from './pages/CheckoutPage'
import ReservationsPage from './pages/ReservationsPage'
import Navbar from './components/Navbar'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 30_000, retry: 1 },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Navbar />
        <Routes>
          <Route path="/" element={<FlightsPage />} />
          <Route path="/flights/:flightId/seats" element={<SeatMapPage />} />
          <Route path="/checkout" element={<CheckoutPage />} />
          <Route path="/reservations" element={<ReservationsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}