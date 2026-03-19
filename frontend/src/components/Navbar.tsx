import { useNavigate, useLocation } from 'react-router-dom'

export default function Navbar() {
  const navigate = useNavigate()
  const location = useLocation()

  const links = [
    { path: '/', label: '✈ Flights' },
    { path: '/reservations', label: '📋 My Reservations' },
  ]

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <div className="navbar-logo">FREIGHTOS</div>
        <div className="navbar-links">
          {links.map((link) => (
            <button
              key={link.path}
              className={`navbar-link ${location.pathname === link.path ? 'active' : ''}`}
              onClick={() => navigate(link.path)}
            >
              {link.label}
            </button>
          ))}
        </div>
      </div>
    </nav>
  )
}