const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api'

export async function fetchHallLayout(showId) {
  const res = await fetch(`${API_BASE}/hall-layout/${showId}/`)
  if (!res.ok) {
    throw new Error('Failed to load hall layout')
  }
  return res.json()
}

export async function holdSeat({ userId, seatId, showId }) {
  const res = await fetch(`${API_BASE}/hold-seat/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      user_id: Number(userId),
      seat_id: Number(seatId),
      show_id: Number(showId)
    })
  })

  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    const message = data.detail || 'Hold failed'
    const error = new Error(message)
    error.status = res.status
    throw error
  }

  return res.json()
}

export async function bookSeat({ userId, seatId, showId }) {
  const res = await fetch(`${API_BASE}/book-seat/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      user_id: Number(userId),
      seat_id: Number(seatId),
      show_id: Number(showId)
    })
  })

  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    const message = data.detail || 'Booking failed'
    const error = new Error(message)
    error.status = res.status
    throw error
  }

  return res.json()
}
