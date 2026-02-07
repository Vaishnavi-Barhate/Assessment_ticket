import { useEffect, useMemo, useState } from 'react'
import { bookSeat, fetchHallLayout, holdSeat } from './api'
import './index.css'

const statusLabels = {
  available: 'Available',
  held: 'Held',
  booked: 'Booked'
}

export default function App() {
  const [showId, setShowId] = useState(1)
  const [userId, setUserId] = useState(1)
  const [layout, setLayout] = useState(null)
  const [selectedSeatId, setSelectedSeatId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const rows = useMemo(() => {
    if (!layout) return []
    const byRow = new Map()
    layout.seats.forEach((seat) => {
      const row = seat.row
      if (!byRow.has(row)) byRow.set(row, [])
      byRow.get(row).push(seat)
    })
    return Array.from(byRow.entries()).map(([row, seats]) => ({
      row,
      seats: seats.sort((a, b) => a.number - b.number)
    }))
  }, [layout])

  async function loadLayout({ keepSelection = false, preferredSeatId = null } = {}) {
    setLoading(true)
    setMessage('')
    try {
      const data = await fetchHallLayout(showId)
      setLayout(data)
      if (keepSelection) {
        const seatId = preferredSeatId ?? selectedSeatId
        const seat = data.seats.find((item) => item.id === seatId)
        if (!seat) {
          setSelectedSeatId(null)
        } else if (seat.status === 'booked') {
          setSelectedSeatId(null)
        } else if (seat.status === 'held' && seat.locked_by && seat.locked_by !== Number(userId)) {
          setSelectedSeatId(null)
        } else {
          setSelectedSeatId(seatId)
        }
      } else {
        setSelectedSeatId(null)
      }
    } catch (err) {
      setMessage(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadLayout()
  }, [])

  function isSelectable(seat) {
    if (seat.status === 'booked') return false
    if (seat.status === 'held' && seat.locked_by && seat.locked_by !== Number(userId)) return false
    return true
  }

  async function handleHold(seat) {
    if (!isSelectable(seat)) return
    if (seat.status === 'held' && seat.locked_by === Number(userId)) {
      setSelectedSeatId(seat.id)
      return
    }
    setLoading(true)
    setMessage('')
    try {
      await holdSeat({ userId, seatId: seat.id, showId })
      await loadLayout({ keepSelection: true, preferredSeatId: seat.id })
    } catch (err) {
      setMessage(err.message)
      await loadLayout()
    } finally {
      setLoading(false)
    }
  }

  async function handleBook() {
    if (!selectedSeatId) return
    setLoading(true)
    setMessage('')
    try {
      await bookSeat({ userId, seatId: selectedSeatId, showId })
      setMessage('Booking confirmed.')
      await loadLayout()
    } catch (err) {
      setMessage(err.message)
      await loadLayout()
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div>
          <p className="eyebrow">High-Volume Ticketing Engine</p>
          <h1>Seat Booking Console</h1>
          <p className="subtext">Real-time hall layout with concurrency-safe booking.</p>
        </div>
        <div className="controls">
          <label>
            Show ID
            <input value={showId} onChange={(e) => setShowId(Number(e.target.value))} type="number" />
          </label>
          <label>
            User ID
            <input value={userId} onChange={(e) => setUserId(Number(e.target.value))} type="number" />
          </label>
          <button onClick={loadLayout} disabled={loading}>Load Layout</button>
        </div>
      </header>

      {layout && (
        <section className="meta">
          <div>
            <span>Venue</span>
            <strong>{layout.venue_name}</strong>
          </div>
          <div>
            <span>Hall</span>
            <strong>{layout.hall_name}</strong>
          </div>
          <div>
            <span>Movie</span>
            <strong>{layout.movie_title}</strong>
          </div>
          <div>
            <span>Starts</span>
            <strong>{new Date(layout.starts_at).toLocaleString()}</strong>
          </div>
        </section>
      )}

      <section className="layout">
        {rows.map((row) => (
          <div className="row" key={row.row}>
            <span className="row-label">Row {row.row}</span>
            <div className="seats">
              {row.seats.map((seat) => {
                const selected = seat.id === selectedSeatId
                const selectable = isSelectable(seat)
                const className = [
                  'seat',
                  `seat-${seat.status}`,
                  selected ? 'seat-selected' : '',
                  selectable ? '' : 'seat-disabled'
                ].join(' ')
                return (
                  <button
                    key={seat.id}
                    className={className}
                    onClick={() => handleHold(seat)}
                    disabled={!selectable}
                    title={`Seat ${seat.row}${seat.number} - ${statusLabels[seat.status]}`}
                  >
                    {seat.row}{seat.number}
                  </button>
                )
              })}
            </div>
          </div>
        ))}
      </section>

      <section className="actions">
        <div className="legend">
          <span className="legend-item available">Available</span>
          <span className="legend-item held">Held</span>
          <span className="legend-item booked">Booked</span>
          <span className="legend-item selected">Your Selection</span>
        </div>
        <button onClick={handleBook} disabled={!selectedSeatId || loading}>Book Selected Seat</button>
      </section>

      {message && <p className="message">{message}</p>}
    </div>
  )
}
