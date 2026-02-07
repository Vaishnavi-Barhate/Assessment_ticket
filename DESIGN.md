# Ticket Booking Platform — System Design

## Overview
This system supports high‑volume movie ticket booking with strong consistency under concurrent requests. The core entity is **ShowSeat**, which represents a seat’s state for a specific showtime.

## ER Diagram (Text)
```
User (id, username, ...)
Venue (id, name, city)
  1 ──< Hall (id, venue_id, name)
          1 ──< Seat (id, hall_id, row, number)
          1 ──< Showtime (id, hall_id, movie_id, starts_at, ends_at)
Movie (id, title, duration_minutes)
Showtime 1 ──< ShowSeat (id, showtime_id, seat_id, status, locked_by_id, locked_until, booked_at)
Showtime 1 ──< Booking (id, showtime_id, seat_id, user_id, created_at)
```

## Theoretical Database Schema

### Entities
- **Venue**: group of halls
- **Hall**: physical screening hall inside a venue
- **Seat**: physical seat in a hall (row + number)
- **Movie**: film metadata
- **Showtime**: movie scheduled in a hall at a time window
- **ShowSeat**: seat state for a showtime (available/held/booked)
- **Booking**: immutable booking record for a user, showtime, seat
- **User**: Django auth user

### Constraints & Indexes
- `Seat`: unique `(hall_id, row, number)`
- `ShowSeat`: unique `(showtime_id, seat_id)`
- `Booking`: unique `(showtime_id, seat_id)`
- Indexes:
  - `Seat(hall_id, row, number)` for layout ordering
  - `Showtime(hall_id, starts_at)` for schedule browsing
  - `ShowSeat(showtime_id, status)` for fast layout reads
  - `Booking(showtime_id, created_at)` for reporting

## Seat State Model
`ShowSeat.status`:
- `available`: free to hold or book
- `held`: reserved for a user until `locked_until`
- `booked`: confirmed booking

Expired holds are released on `GET /hall-layout` and on booking/hold attempts. A background job can also release holds periodically for larger scale.

## Decision: Locking System
**Chosen strategy:** Pessimistic row‑level locking using `SELECT ... FOR UPDATE` on the `ShowSeat` row, plus a unique constraint on `Booking(showtime_id, seat_id)`.

**Why this is efficient and correct**
- Guarantees a single writer for a seat row during contention.
- Eliminates race conditions where multiple users book the same seat.
- Row‑level locks are scoped to the exact seat row (not the entire table), allowing high concurrency across different seats.
- The unique constraint is a final safety net against double booking.

## Data Flow
1. **User selects show** in the UI.
2. UI calls `GET /hall-layout/{show_id}`.
3. Backend fetches `ShowSeat` list with `select_related` and returns seat states.
4. UI calls `POST /hold-seat` when a seat is clicked.
5. Backend locks the row and sets `held` with `locked_until`.
6. UI calls `POST /book-seat` to confirm payment and booking.
7. Backend locks the row again, validates state, writes booking and marks `booked`.

## API Flow (Frontend → Backend → DB)
1. UI calls `GET /hall-layout/{show_id}` to render the grid.
2. Clicking a seat calls `POST /hold-seat` (sets `held` + `locked_until`).
3. Confirming calls `POST /book-seat` (sets `booked` + creates `Booking`).
4. If a conflict occurs, API returns `409` and UI refreshes.

## API Design

### 1) Get Hall Layout
**GET** `/api/hall-layout/{show_id}/`

**Response** `200`
```json
{
  "show_id": 1,
  "hall_name": "Hall 1",
  "venue_name": "Metro Cineplex",
  "movie_title": "Release Night",
  "starts_at": "2026-02-08T14:30:00Z",
  "seats": [
    {
      "id": 101,
      "row": "A",
      "number": 1,
      "status": "available",
      "locked_by": null,
      "locked_until": null
    }
  ]
}
```

### 2) Hold a Seat (5 minutes)
**POST** `/api/hold-seat/`

**Request**
```json
{
  "user_id": 1,
  "seat_id": 101,
  "show_id": 1
}
```

**Response** `200`
```json
{
  "detail": "Seat held."
}
```

**Failure** `409`
```json
{
  "detail": "Seat currently held by another user."
}
```

### 3) Book a Seat
**POST** `/api/book-seat/`

**Request**
```json
{
  "user_id": 1,
  "seat_id": 101,
  "show_id": 1
}
```

**Response** `201`
```json
{
  "detail": "Booking confirmed."
}
```

**Failure** `409`
```json
{
  "detail": "Seat already booked."
}
```

## System Design Optimizations
- `ShowSeat` acts as a precomputed seat state table for fast read‑heavy access.
- Layout query uses `select_related` and `values()` to avoid N+1.
- Indexes on `ShowSeat(showtime_id, status)` keep layout fetches fast.
- Row‑level locking avoids blocking unrelated seats.

## Conflict Resolution Techniques
- **Pessimistic locking** ensures only one transaction can modify a seat row at a time.
- **Unique constraint** on `(showtime_id, seat_id)` prevents double booking even under edge races.
- **Explicit 409 responses** make conflicts clear and allow the UI to refresh immediately.
