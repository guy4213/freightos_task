# ✈ Freightos Flight Seat Reservation

A full-stack flight seat reservation system built with **FastAPI** (backend) and **React + Vite** (frontend).

---

## 🏗️ Architecture

```
freightos_task/
├── backend/    ← FastAPI + PostgreSQL
└── frontend/   ← React + Vite + TypeScript
```

Both services run independently. The frontend communicates with the backend via REST API.

---

## ⚙️ Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Docker** (for PostgreSQL)

---

## 🚀 Quick Start

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

# Create .env file
cp .env.example .env
# Edit .env if your DB credentials differ from defaults

# Seed the database (creates tables + 4 flights with 60 seats each)
python -m app.seed

# Start the server
uvicorn app.main:app --reload
```

Backend runs at: **http://localhost:8000**
Interactive API docs: **http://localhost:8000/docs**

---

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

Frontend runs at: **http://localhost:5173**

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/flights` | List all available flights |
| `GET` | `/api/flights/:id/seats` | Get seat map for a flight |
| `POST` | `/api/bookings` | Create a new booking |
| `GET` | `/api/bookings?session_id=xxx` | Get all bookings for a session |
| `PATCH` | `/api/bookings/:id/cancel` | Cancel a booking |

---

## 🗺️ Application Flow

1. **Flights Page** — Browse available flights
2. **Seat Map Page** — Select seats (10 rows × 6 columns, 60 seats total)
3. **Checkout Page** — Fill in passenger details for each seat
4. **Reservations Page** — View and manage your bookings

---

## 💺 Seat Types & Pricing

| Column | Type | Price |
|--------|------|-------|
| A, F | Window | $200 |
| B, E | Middle | $150 |
| C, D | Aisle | $100 |

---

## ✅ Business Rules

- Maximum **9 seats** per booking
- Maximum **1 infant per adult** (infants = under 2 years old)
- Infants do **not** affect pricing
- Each passenger must have a **unique name and phone number** within a booking
- The **same passenger** (name + DOB + phone) cannot be booked twice on the same flight
- Seat availability is **enforced at the database level** — concurrent bookings are handled safely

---

## 🧪 Running Tests

### Backend — Unit + Integration (33 tests)
```bash
cd backend

# Make sure venv is active
python -m pytest tests/ -v
```

Test coverage:
- **Unit tests** — infant detection, age calculation, ratio validation
- **Integration tests** — full HTTP flow for all 5 endpoints, concurrency guards, validation rules

---

### Frontend — E2E Tests (6 tests)
```bash
# Make sure both backend and frontend are running, then:
cd frontend
npx playwright test
```

E2E coverage:
- Flights list renders correctly
- Navigation to seat map
- Seat selection + live summary update
- Full booking flow (select → checkout → confirm → reservations)
- Reserved seat is disabled after booking
- Cancel booking flow

## 🗄️ Database

**PostgreSQL** is required for production.
The seed script auto-creates all tables and populates 4 sample flights.

`.env` file format:
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/freightos_db
```

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app + CORS
│   ├── config.py            # Environment config
│   ├── database.py          # DB connection + session
│   ├── seed.py              # DB seeding script
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── routers/             # HTTP route handlers
│   └── services/            # Business logic layer
└── tests/
    ├── conftest.py          # Test fixtures + SQLite test DB
    ├── test_unit.py         # Pure unit tests
    └── test_integration.py  # API integration tests

frontend/
└── src/
    ├── pages/               # FlightsPage, SeatMapPage, CheckoutPage, ReservationsPage
    ├── components/          # Navbar
    ├── store/               # Zustand booking state
    ├── api/                 # Fetch functions
    ├── types/               # TypeScript interfaces
    └── utils/               # Session ID management
```