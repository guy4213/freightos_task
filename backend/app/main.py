from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
 
from app.routers import flights, bookings
 
app = FastAPI(title="Freightos Flight Booking API", version="1.0.0")
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
app.include_router(flights.router)
app.include_router(bookings.router)
 
 
@app.get("/health")
def health():
    return {"status": "ok"}
 