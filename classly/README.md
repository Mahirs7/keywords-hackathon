# Classly - Unified Learning Dashboard

A Next.js + Flask application that aggregates coursework from Canvas, Gradescope, PrairieLearn, and more into a single dashboard.

## Features

- **Dashboard**: View all your upcoming deadlines and today's schedule
- **Platform Integration**: Connect Canvas, Gradescope, Campuswire, PrairieLearn
- **Course Assistant (RAG)**: Ask questions about your course materials using AI-powered retrieval

## Tech Stack

- **Frontend**: Next.js 14 (App Router), React, TypeScript, Tailwind CSS
- **Backend**: Flask (Python), REST API
- **Database**: Supabase (PostgreSQL + pgvector for RAG)
- **Auth**: Supabase Auth

---

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.9+
- A Supabase project

### 1. Clone and Install

```bash
# Install frontend dependencies
cd classly
npm install

# Install backend dependencies
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

**Frontend** (`.env.local`):
```bash
cp .env.local.example .env.local
# Edit with your Supabase credentials
```

**Backend** (`backend/.env`):
```bash
cp backend/.env.example backend/.env
# Edit with your Supabase credentials and optionally OpenAI key
```

### 3. Set Up Database

1. Go to your Supabase Dashboard → SQL Editor
2. Run the contents of `supabase/schema.sql`
3. This creates all tables including RAG tables with pgvector

### 4. Seed Mock Data (for RAG)

```bash
cd classly
python scripts/seed_supabase_mock.py
```

This populates:
- 3 courses (CS225, CS374, CS421)
- Sample documents (syllabi, assignments, office hours)
- Vector embeddings for similarity search

### 5. Run the App

**Terminal 1 - Backend:**
```bash
cd classly/backend
python app.py
# Runs on http://localhost:5000
```

**Terminal 2 - Frontend:**
```bash
cd classly
npm run dev
# Runs on http://localhost:3000
```

### 6. Use the Course Assistant

1. Navigate to http://localhost:3000
2. Log in (or sign up via Supabase Auth)
3. Click "Course Assistant" in the sidebar
4. Select a course and ask questions like:
   - "What are the upcoming assignments?"
   - "When are office hours?"
   - "What's the grading policy?"

---

## RAG Feature Details

The Course Assistant uses Retrieval-Augmented Generation:

1. **Embedding**: Query is converted to a vector (OpenAI or deterministic fallback)
2. **Retrieval**: Similar chunks are found via pgvector cosine similarity
3. **Generation**: Answer is synthesized from retrieved context (OpenAI or mock)

### With OpenAI Key
- Real semantic embeddings (text-embedding-ada-002)
- LLM-powered answers (gpt-3.5-turbo)

### Without OpenAI Key
- Deterministic hash-based embeddings (works for testing)
- Answers synthesized directly from retrieved chunks

---

## Project Structure

```
classly/
├── app/                    # Next.js App Router
│   ├── (dashboard)/       # Dashboard pages
│   │   ├── assistant/     # RAG Course Assistant page
│   │   ├── home/
│   │   └── ...
│   ├── components/        # React components
│   └── lib/               # Utilities, hooks, Supabase client
├── backend/               # Flask API
│   ├── app.py            # Main Flask app
│   ├── routes/           # API route blueprints
│   │   ├── rag.py        # RAG endpoints
│   │   └── ...
│   └── requirements.txt
├── scripts/
│   └── seed_supabase_mock.py  # Mock data seeder
└── supabase/
    ├── schema.sql        # Database schema
    └── README.md         # Supabase setup guide
```

---

## API Endpoints

### RAG Endpoints (`/api/rag`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/rag/courses` | List available courses |
| POST | `/api/rag/ask` | Ask a question about a course |
| GET | `/api/rag/health` | Check RAG service status |

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/rag/ask \
  -H "Content-Type: application/json" \
  -d '{"courseCode": "CS225", "question": "What are the upcoming assignments?"}'
```

---

## Troubleshooting

### "No courses available"
Run the seed script: `python scripts/seed_supabase_mock.py`

### "Failed to connect to server"
Make sure the Flask backend is running on port 5000

### Vector search not working
1. Ensure pgvector extension is enabled: `CREATE EXTENSION IF NOT EXISTS vector;`
2. Check that chunks have embeddings in `course_chunks` table

---

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Supabase Documentation](https://supabase.com/docs)
- [pgvector](https://github.com/pgvector/pgvector)
