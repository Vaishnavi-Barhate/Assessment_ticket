# Ticket Booking Platform (Django + DRF + React)

Concurrency‑safe ticket booking with PostgreSQL, DRF APIs, and a React seat map UI.

## Architecture
See `DESIGN.md` for ER diagram, API flow, and locking strategy.

## Quick Start (Local)

### Backend
```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Set database env vars:
```bash
export POSTGRES_DB=ticketing
export POSTGRES_USER=ticketing
export POSTGRES_PASSWORD=ticketing
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
```

Run migrations and seed:
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

API runs at `http://localhost:8000/api/`.

### Frontend
```bash
cd ../frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

Optional API base:
```bash
export VITE_API_BASE=http://localhost:8000/api
```

## Test Environment (Demo Run)

This is a simple test setup for local evaluation:

1. Ensure PostgreSQL is running and the `ticketing` database/user exist.
2. Run backend and frontend with the steps above.
3. Create two users to simulate concurrency:
```bash
cd backend
python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); print(User.objects.create_user(username='user1', password='user1').id)"
python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); print(User.objects.create_user(username='user2', password='user2').id)"
```
4. In the UI, set **User ID** to `user1` and hold a seat (yellow).
5. Change **User ID** to `user2` and confirm the same seat is blocked.

## API Endpoints
- `GET /api/hall-layout/{show_id}/`
- `POST /api/hold-seat/`
- `POST /api/book-seat/`

## Notes
- Booking uses PostgreSQL row‑level locking via `select_for_update()` plus unique constraints.
- Hold duration is 5 minutes (`locked_until`).
- Expired holds are released on read/write. A scheduled cleanup can be added for scale.
