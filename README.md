# ✈ Freightos Flight Seat Reservation

A production-oriented fullstack flight booking system — built as a technical assignment for Freightos.

Users can browse flights, select seats from an interactive map, fill in passenger details, and manage their reservations — all in a clean, session-based flow with no authentication required.

---

## 🏗️ Architecture

```
freightos_task/
├── backend/     ← FastAPI + PostgreSQL + SQLAlchemy
└── frontend/    ← React 19 + Vite + TypeScript
```

Both services are **independently runnable**. The frontend communicates with the backend over a REST API. Session identity is established via a UUID stored in `localStorage` and sent as an `X-Session-ID` header on every request.

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI (Python) |
| Database | PostgreSQL (via Docker) |
| ORM | SQLAlchemy 2.0 |
| Validation | Pydantic v2 |
| Frontend | React 19 + Vite 8 + TypeScript |
| State | Zustand |
| Data Fetching | TanStack Query v5 |
| Routing | React Router v7 |
| Testing (BE) | Pytest — unit + integration (33 tests) |
| Testing (FE) | Playwright E2E (6 tests) |

---

## 💺 Seat Types & Pricing

| Column | Type | Price |
|--------|------|-------|
| A, F | Window | $200 |
| B, E | Middle | $150 |
| C, D | Aisle | $100 |

> Pricing is **calculated exclusively on the backend** — the frontend never sends or determines prices.

---

## ✅ Business Rules

- Max **9 seats** per booking
- Max **1 infant per adult** (infant = under 2 years old based on DOB)
- Infants **do not affect pricing**
- Each passenger must have a **unique name and phone number** within the same booking
- The **same passenger** (name + DOB + phone) cannot book the same flight twice
- Seat availability is enforced with **`SELECT FOR UPDATE` row-locking** to handle concurrent requests safely

---

## 🔄 Application Flow

```
Flights Page → Seat Map → Checkout → Reservations
```

1. **Flights Page** — Browse 4 seeded flights with live available seat counts
2. **Seat Map Page** — 10×6 interactive grid with color-coded seat types, hover tooltips, and a live summary sidebar
3. **Checkout Page** — Per-seat passenger forms with full client-side and server-side validation
4. **Reservations Page** — Session-scoped booking history with a view modal and cancel action

---

## 🧠 Session Management

Since this system has no authentication:

- On first visit, the frontend generates a UUID and saves it to `localStorage`
- Every API request includes this UUID as `X-Session-ID` header
- The backend links all bookings to this session ID
- Each user only sees their own bookings

This is explicitly **not production-secure** — it's designed to be easily swapped out for real auth (JWT / OAuth) later.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker

---

### 1. Start the Database

```bash
docker run --name postgres-db \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=freightos_db \
  -p 5432:5432 \
  -d postgres
```

---

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Seed database (creates tables + 4 flights with 60 seats each)
python -m app.seed

# Start the server
uvicorn app.main:app --reload
```

Backend runs at **http://localhost:8000**  
Interactive docs at **http://localhost:8000/docs**

---

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at **http://localhost:5173**

---

## 🌐 API Reference

> All booking endpoints require an `X-Session-ID` header containing a valid UUID.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/flights` | List all flights with available seat count |
| `GET` | `/api/flights/:id/seats` | Get the seat map for a specific flight |
| `POST` | `/api/bookings` | Create a new booking |
| `GET` | `/api/bookings` | Get all bookings for the current session |
| `PATCH` | `/api/bookings/:id/cancel` | Cancel a booking (session-verified) |

---

## 🧪 Running Tests

### Backend — Unit + Integration (33 tests)

```bash
cd backend

# Make sure venv is active
python -m pytest tests/ -v
```

Coverage:
- **Unit tests** — infant detection, age calculation, ratio validation
- **Integration tests** — full HTTP flow, concurrency guards, all validation rules

---

### Frontend — E2E (6 tests)

```bash
# Backend and frontend must both be running
cd frontend
npx playwright test
```

Coverage:
- Flights list renders correctly
- Seat map navigation
- Seat selection + live sidebar update
- Full booking flow (select → checkout → confirm → reservations)
- Reserved seat is disabled after booking
- Cancel booking flow

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point + CORS
│   ├── config.py            # Environment config (pydantic-settings)
│   ├── database.py          # SQLAlchemy engine + session
│   ├── dependencies.py      # X-Session-ID header extraction
│   ├── exceptions.py        # Typed AppError exceptions
│   ├── seed.py              # DB seeding (4 flights × 60 seats)
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── routers/             # HTTP route handlers
│   └── services/            # All business logic (booking_service.py)
└── tests/
    ├── conftest.py           # SQLite test DB + fixtures
    ├── test_unit.py          # Pure unit tests
    └── test_integration.py   # Full API integration tests

frontend/
└── src/
    ├── pages/               # FlightsPage, SeatMapPage, CheckoutPage, ReservationsPage
    ├── components/          # Navbar
    ├── store/               # Zustand booking state
    ├── api/                 # Typed fetch functions + central API client
    ├── types/               # TypeScript interfaces
    └── utils/               # Session ID management
```

---

## ⚠️ Concurrency Handling

Concurrent seat bookings are handled with PostgreSQL row-level locking:

```python
db.query(Seat).filter(Seat.id.in_(seat_ids)).with_for_update().all()
```

If two users attempt to book the same seat simultaneously, only one succeeds — the other receives a `409 Conflict` error with a clear message.

---

## 🗄️ Environment Variables

**Backend** (`.env`):
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/freightos_db
```

**Frontend** (`.env`):
```
VITE_BASE_URL=http://localhost:8000
```

---

## 📈 Potential Future Improvements

- 🔐 Real authentication (JWT / OAuth2)
- 💳 Payment integration
- 🪑 Temporary seat holds (e.g. 10-minute reservation locks)
- 📊 Admin dashboard
- 🌍 Containerized deployment (Docker Compose)
- ✉️ Email booking confirmations

---

## 🧑‍💻 Author

Built by **Guy Franses** as a fullstack system design assignment.