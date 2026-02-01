# Supabase Setup for Classly RAG

This document explains how to set up the Supabase database for the RAG Course Q&A feature.

## Prerequisites

1. A Supabase project (create one at [supabase.com](https://supabase.com))
2. Python 3.9+ with pip
3. Environment variables configured

## Step 1: Enable pgvector Extension

Go to your Supabase dashboard → SQL Editor, and run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

> **Note**: pgvector is pre-installed on Supabase. This just enables it.

## Step 2: Run the Schema

1. Open the Supabase SQL Editor in your dashboard
2. Copy the contents of `schema.sql` 
3. Run the entire script

Alternatively, use the Supabase CLI:
```bash
supabase db push
```

## Step 3: Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Required for RAG
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Optional: For real embeddings and LLM responses
OPENAI_API_KEY=sk-your-openai-key
```

### Getting Your Keys

1. **SUPABASE_URL**: Go to Project Settings → API → Project URL
2. **SUPABASE_SERVICE_ROLE_KEY**: Go to Project Settings → API → `service_role` key (keep this secret!)
3. **OPENAI_API_KEY** (optional): Get from [platform.openai.com](https://platform.openai.com/api-keys)

## Step 4: Seed Mock Data

Run the seed script to populate mock course data:

```bash
cd classly
python scripts/seed_supabase_mock.py
```

This will:
- Create 3 courses: CS225, CS374, CS421
- Add sample documents (syllabus, assignments, office hours, etc.)
- Generate embeddings for vector search
- Insert chunks into the database

## RAG Tables Overview

| Table | Description |
|-------|-------------|
| `rag_courses` | Available courses for Q&A (code, name) |
| `course_documents` | Full documents per course (syllabus, guides, etc.) |
| `course_chunks` | Chunked text with vector embeddings for similarity search |

## RPC Functions

### `match_course_chunks`

Find similar chunks for a specific course:

```sql
SELECT * FROM match_course_chunks(
  'course-uuid-here',
  '[0.1, 0.2, ...]'::vector(1536),  -- query embedding
  6,    -- max results
  0.75  -- min similarity threshold
);
```

### `match_all_course_chunks`

Find similar chunks across all courses:

```sql
SELECT * FROM match_all_course_chunks(
  '[0.1, 0.2, ...]'::vector(1536),
  6,
  0.75
);
```

## Troubleshooting

### "extension vector does not exist"
Run `CREATE EXTENSION IF NOT EXISTS vector;` in SQL Editor.

### "permission denied for table"
Make sure you're using the `service_role` key, not the `anon` key.

### Embeddings not working
If OPENAI_API_KEY is not set, the seed script uses deterministic fake embeddings based on content hashes. These work for testing but won't provide meaningful semantic search.

## Security Notes

- **Never expose `SUPABASE_SERVICE_ROLE_KEY` to the frontend**
- The frontend calls Flask backend, which uses the service role key to query Supabase
- RAG tables don't have RLS enabled by default (add policies if needed for multi-tenant use)
