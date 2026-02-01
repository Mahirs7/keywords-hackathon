# StudyHub Backend

Flask API server for StudyHub - the unified student coursework dashboard.

## Setup

1. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy environment variables:
```bash
cp .env.example .env
# Edit .env with your actual values
```

4. Run the server:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Health Check
- `GET /` - API info
- `GET /api/health` - Health check

### Deadlines
- `GET /api/deadlines/` - All deadlines
- `GET /api/deadlines/upcoming` - Upcoming deadlines
- `GET /api/deadlines/today` - Today's deadlines
- `GET /api/deadlines/:id` - Specific deadline

### Schedule
- `GET /api/schedule/` - Full schedule
- `GET /api/schedule/today` - Today's schedule
- `GET /api/schedule/week` - This week's schedule
- `POST /api/schedule/` - Add schedule item
- `DELETE /api/schedule/:id` - Remove schedule item

### Platforms
- `GET /api/platforms/` - All connected platforms
- `GET /api/platforms/summary` - Dashboard summary stats
- `GET /api/platforms/:id` - Platform details
- `POST /api/platforms/:id/sync` - Trigger platform sync
- `POST /api/platforms/connect` - Connect new platform

### Auth
- `GET /api/auth/me` - Current user
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/preferences` - Get preferences
- `PUT /api/auth/preferences` - Update preferences

### Course Sync on Login
When `POST /api/auth/login` is called, the backend resolves the user’s enrolled courses
against the mock `all_classes` table and stores the resulting course IDs on the user
object as `courses`.

## Architecture

```
backend/
├── app.py              # Flask app entry point
├── routes/
│   ├── auth.py         # Authentication routes
│   ├── deadlines.py    # Deadline aggregation
│   ├── platforms.py    # Per-platform data
│   └── schedule.py     # Schedule management
├── scrapers/           # Platform scrapers (to be added)
│   ├── canvas.py
│   ├── gradescope.py
│   ├── campuswire.py
│   └── prairielearn.py
├── services/           # Business logic (to be added)
│   └── supabase.py
└── requirements.txt
```
