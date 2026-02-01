#!/usr/bin/env python3
"""
Seed script for Classly RAG Course Q&A
Creates mock courses, documents, and embeddings in Supabase

Usage:
    python scripts/seed_supabase_mock.py

Environment:
    SUPABASE_URL - Your Supabase project URL
    SUPABASE_SERVICE_ROLE_KEY - Service role key (not anon!)
    OPENAI_API_KEY - (Optional) For real embeddings
"""

import os
import sys
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

# Load environment from backend/.env
backend_env = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', '.env')
load_dotenv(backend_env)

from supabase import create_client, Client

# Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

EMBEDDING_DIM = 1536
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# ============================================
# Mock Course Data
# ============================================

MOCK_COURSES = [
    {
        "code": "CS225",
        "name": "Data Structures",
        "documents": [
            {
                "title": "CS225 Syllabus",
                "source": "syllabus",
                "content": """
CS225: Data Structures - Spring 2026 Syllabus

Course Overview:
This course covers fundamental data structures and algorithms. Topics include arrays, linked lists, stacks, queues, trees, graphs, hash tables, and sorting algorithms.

Instructors:
- Professor Carl Evans (cevans@illinois.edu) - Lectures
- Professor Brad Solomon (bsolomon@illinois.edu) - Labs

Office Hours:
- Professor Evans: Monday & Wednesday 2-4 PM, Siebel 2208
- Professor Solomon: Tuesday & Thursday 3-5 PM, Siebel 2209
- TAs: Check course website for full schedule

Grading Policy:
- MPs (Machine Problems): 35%
- Labs: 15%
- Midterm Exams (2): 20%
- Final Exam: 25%
- Participation: 5%

Late Policy:
- MPs: 10% penalty per day, max 3 days late
- Labs: No late submissions accepted
- Exams: No makeup without prior approval

Academic Integrity:
All work must be your own. Collaboration is allowed on understanding concepts, but code must be written independently. Use of AI coding assistants must be disclosed.

Required Materials:
- Textbook: "Introduction to Algorithms" (CLRS)
- C++ compiler (g++ recommended)
- Git for version control
"""
            },
            {
                "title": "CS225 Assignments",
                "source": "assignments",
                "content": """
CS225 Assignment Schedule - Spring 2026

MP1: PNG Image Manipulation
Due: February 7, 2026 at 11:59 PM
Topics: Classes, memory management, file I/O
Description: Implement image transformations including rotation, scaling, and color filters.
Points: 100

MP2: Linked Lists
Due: February 21, 2026 at 11:59 PM
Topics: Pointers, linked list operations, iterators
Description: Build a doubly-linked list with insertion, deletion, and reversal operations.
Points: 100

MP3: Binary Trees
Due: March 7, 2026 at 11:59 PM
Topics: Tree traversal, BST operations, balancing
Description: Implement a self-balancing AVL tree with search and insert operations.
Points: 150

MP4: Hash Tables
Due: March 21, 2026 at 11:59 PM
Topics: Hash functions, collision resolution, dynamic resizing
Description: Build a hash table with chaining and analyze performance.
Points: 100

MP5: Graphs
Due: April 11, 2026 at 11:59 PM
Topics: Graph representations, BFS, DFS, shortest paths
Description: Implement graph algorithms including Dijkstra's algorithm.
Points: 150

MP6: Final Project - Image Mosaics
Due: April 25, 2026 at 11:59 PM
Topics: K-d trees, nearest neighbor search
Description: Create image mosaics using k-d tree spatial indexing.
Points: 200
"""
            },
            {
                "title": "CS225 Exam Information",
                "source": "exams",
                "content": """
CS225 Exam Schedule and Topics

Midterm 1:
Date: February 27, 2026, 7-9 PM
Location: ECEB 1002
Topics Covered:
- Big-O notation and complexity analysis
- Arrays and memory allocation
- Linked lists (singly, doubly, circular)
- Stacks and queues
- Tree basics and traversals

Format: 10 multiple choice, 4 written problems
Allowed Materials: One 8.5x11 handwritten cheat sheet (both sides)

Midterm 2:
Date: April 3, 2026, 7-9 PM
Location: ECEB 1002
Topics Covered:
- Binary search trees
- AVL trees and rotations
- Hash tables
- Heaps and priority queues
- Graph basics

Format: 10 multiple choice, 4 written problems
Allowed Materials: One 8.5x11 handwritten cheat sheet (both sides)

Final Exam:
Date: May 8, 2026, 1:30-4:30 PM
Location: State Farm Center
Topics: Cumulative, emphasis on:
- Graph algorithms (BFS, DFS, Dijkstra, MST)
- Algorithm analysis
- Data structure comparisons

Format: 20 multiple choice, 6 written problems
Allowed Materials: Two 8.5x11 handwritten cheat sheets (both sides)
"""
            },
            {
                "title": "CS225 Office Hours Schedule",
                "source": "office_hours",
                "content": """
CS225 Office Hours - Spring 2026

Location: Siebel 0220 (Basement Lab) unless otherwise noted

Monday:
- 10:00 AM - 12:00 PM: TA Jessica Wu
- 2:00 PM - 4:00 PM: Professor Evans (Siebel 2208)
- 6:00 PM - 8:00 PM: TA Marcus Chen

Tuesday:
- 11:00 AM - 1:00 PM: TA Ryan Park
- 3:00 PM - 5:00 PM: Professor Solomon (Siebel 2209)
- 7:00 PM - 9:00 PM: TA Aisha Johnson

Wednesday:
- 10:00 AM - 12:00 PM: TA David Kim
- 2:00 PM - 4:00 PM: Professor Evans (Siebel 2208)
- 6:00 PM - 8:00 PM: TA Sarah Martinez

Thursday:
- 11:00 AM - 1:00 PM: TA Emily Thompson
- 3:00 PM - 5:00 PM: Professor Solomon (Siebel 2209)
- 7:00 PM - 9:00 PM: TA Alex Rivera

Friday:
- 10:00 AM - 12:00 PM: TA Jordan Lee
- 2:00 PM - 4:00 PM: TA Megan Brown

Saturday:
- 1:00 PM - 4:00 PM: Open lab hours (rotating TAs)

Sunday:
- 5:00 PM - 8:00 PM: Open lab hours (rotating TAs)

Virtual Office Hours (Zoom):
Available by appointment through course website. Sign up slots released weekly on Monday at 9 AM.
"""
            }
        ]
    },
    {
        "code": "CS374",
        "name": "Introduction to Algorithms & Models of Computation",
        "documents": [
            {
                "title": "CS374 Syllabus",
                "source": "syllabus",
                "content": """
CS374: Introduction to Algorithms & Models of Computation - Spring 2026

Course Overview:
This course introduces fundamental techniques for designing and analyzing algorithms. Topics include divide and conquer, dynamic programming, greedy algorithms, graph algorithms, and computational complexity.

Instructors:
- Professor Jeff Erickson (jeffe@illinois.edu)
- Professor Chandra Chekuri (chekuri@illinois.edu)

Prerequisites:
- CS225 (Data Structures)
- CS173 (Discrete Structures)

Office Hours:
- Professor Erickson: Tuesday & Thursday 10-11:30 AM, Siebel 3230
- Professor Chekuri: Monday & Wednesday 3-4:30 PM, Siebel 3232

Grading:
- Homework (10 sets): 40%
- Midterm Exams (2): 30%
- Final Exam: 30%

Homework Policy:
- Groups of up to 3 students allowed
- Must write solutions independently
- LaTeX submissions preferred
- Due Thursdays at 8 PM

Academic Integrity:
Strict policy on collaboration. You may discuss high-level ideas but must write solutions independently. Cite all collaborators and sources.
"""
            },
            {
                "title": "CS374 Homework Schedule",
                "source": "assignments",
                "content": """
CS374 Homework Schedule - Spring 2026

HW1: Big-O and Recurrences
Due: February 6, 2026 at 8:00 PM
Topics: Asymptotic notation, solving recurrences, proof techniques
Problems: 5 problems

HW2: Divide and Conquer
Due: February 13, 2026 at 8:00 PM
Topics: Merge sort analysis, Karatsuba multiplication, closest pair
Problems: 5 problems

HW3: Dynamic Programming I
Due: February 20, 2026 at 8:00 PM
Topics: Edit distance, longest common subsequence, optimal BST
Problems: 5 problems

HW4: Dynamic Programming II
Due: February 27, 2026 at 8:00 PM
Topics: Knapsack, chain matrix multiplication, sequence alignment
Problems: 5 problems

HW5: Greedy Algorithms
Due: March 13, 2026 at 8:00 PM
Topics: Activity selection, Huffman coding, MST algorithms
Problems: 5 problems

HW6: Graph Algorithms I
Due: March 27, 2026 at 8:00 PM
Topics: BFS, DFS, topological sort, strongly connected components
Problems: 5 problems

HW7: Graph Algorithms II
Due: April 3, 2026 at 8:00 PM
Topics: Shortest paths, Dijkstra, Bellman-Ford, Floyd-Warshall
Problems: 5 problems

HW8: Network Flow
Due: April 10, 2026 at 8:00 PM
Topics: Ford-Fulkerson, max-flow min-cut, bipartite matching
Problems: 4 problems

HW9: NP-Completeness
Due: April 17, 2026 at 8:00 PM
Topics: Reduction techniques, NP-complete problems
Problems: 4 problems

HW10: Approximation Algorithms
Due: April 24, 2026 at 8:00 PM
Topics: Vertex cover, set cover, TSP approximations
Problems: 4 problems
"""
            },
            {
                "title": "CS374 Exam Information",
                "source": "exams",
                "content": """
CS374 Exam Schedule and Information

Midterm 1:
Date: March 5, 2026, 7-9 PM
Location: Foellinger Auditorium
Coverage:
- Asymptotic analysis (Big-O, Omega, Theta)
- Recurrence relations
- Divide and conquer algorithms
- Dynamic programming

Midterm 2:
Date: April 9, 2026, 7-9 PM
Location: Foellinger Auditorium
Coverage:
- Greedy algorithms
- Graph algorithms (BFS, DFS, shortest paths)
- Network flow
- Minimum spanning trees

Final Exam:
Date: May 12, 2026, 8-11 AM
Location: Foellinger Auditorium
Coverage: Cumulative, with emphasis on:
- NP-completeness and reductions
- All major algorithm design paradigms
- Proof techniques

Exam Policies:
- No electronic devices
- No notes or cheat sheets
- Problems similar to homework style
- Partial credit awarded for correct approach

Conflict Exams:
Register through CBTF by deadline. Valid conflicts include other exams, religious observances, or documented medical reasons.
"""
            }
        ]
    },
    {
        "code": "CS421",
        "name": "Programming Languages & Compilers",
        "documents": [
            {
                "title": "CS421 Syllabus",
                "source": "syllabus",
                "content": """
CS421: Programming Languages & Compilers - Spring 2026

Course Overview:
Study of programming language features and implementation. Topics include functional programming, type systems, interpreters, and compiler construction.

Instructor:
- Professor Mattox Beckman (mattox@illinois.edu)

Office Hours:
- Professor Beckman: Monday & Wednesday 1-2 PM, Siebel 2112
- TAs: Various times in Siebel 0218

Prerequisites:
- CS233 (Computer Architecture)
- CS374 (Algorithms) recommended

Grading:
- MPs (5): 30%
- Homework/Activities: 10%
- Midterm Exams (2): 30%
- Final Exam: 25%
- Participation: 5%

Languages Used:
- OCaml for functional programming
- We will build interpreters in OCaml
- Some exposure to Haskell for comparison

Required Software:
- OCaml 4.14+
- VSCode with OCaml extension
- Git for assignment submission
"""
            },
            {
                "title": "CS421 Assignments",
                "source": "assignments",
                "content": """
CS421 Machine Problem Schedule - Spring 2026

MP1: OCaml Basics
Due: February 10, 2026 at 11:59 PM
Topics: Pattern matching, recursion, higher-order functions
Description: Implement list manipulation functions in OCaml.
Points: 50

MP2: Algebraic Data Types
Due: February 24, 2026 at 11:59 PM
Topics: Custom types, tree structures, expression trees
Description: Build and evaluate arithmetic expression trees.
Points: 75

MP3: Parser Implementation
Due: March 17, 2026 at 11:59 PM
Topics: Lexing, parsing, AST construction
Description: Build a parser for a simple expression language.
Points: 100

MP4: Type Checker
Due: April 7, 2026 at 11:59 PM
Topics: Type inference, unification, Hindley-Milner
Description: Implement type checking for a small functional language.
Points: 100

MP5: Interpreter
Due: April 28, 2026 at 11:59 PM
Topics: Evaluation, environments, closures
Description: Build a complete interpreter with functions and recursion.
Points: 125

Weekly Activities:
- Due every Friday at 11:59 PM
- Short OCaml programming exercises
- 10 points each (lowest 2 dropped)
"""
            },
            {
                "title": "CS421 Office Hours and Resources",
                "source": "office_hours",
                "content": """
CS421 Office Hours and Resources - Spring 2026

Office Hours Schedule:
Location: Siebel 0218 (unless noted)

Monday:
- 1:00 PM - 2:00 PM: Professor Beckman (Siebel 2112)
- 5:00 PM - 7:00 PM: TA Office Hours

Tuesday:
- 2:00 PM - 4:00 PM: TA Office Hours
- 7:00 PM - 9:00 PM: TA Office Hours

Wednesday:
- 1:00 PM - 2:00 PM: Professor Beckman (Siebel 2112)
- 5:00 PM - 7:00 PM: TA Office Hours

Thursday:
- 2:00 PM - 4:00 PM: TA Office Hours
- 7:00 PM - 9:00 PM: TA Office Hours

Friday:
- 11:00 AM - 1:00 PM: TA Office Hours

Resources:
- Course Website: courses.engr.illinois.edu/cs421
- Piazza: For questions and discussion
- Real World OCaml (online book): Recommended reading
- OCaml documentation: ocaml.org/docs

Study Groups:
Students are encouraged to form study groups. The course facilitates finding study partners through Piazza.

Extra Credit Opportunities:
- Contribute test cases: Up to 5 points per MP
- Fix typos in course materials: 1 point each (max 10)
"""
            },
            {
                "title": "CS421 Exam Information",
                "source": "exams",
                "content": """
CS421 Exam Schedule

Midterm 1:
Date: February 28, 2026, In class
Topics:
- OCaml syntax and semantics
- Pattern matching
- Recursion and tail recursion
- Higher-order functions
- Algebraic data types
Format: Written exam, 75 minutes

Midterm 2:
Date: April 3, 2026, In class
Topics:
- Lexing and parsing
- Context-free grammars
- AST construction
- Type systems basics
- Environment-based evaluation
Format: Written exam, 75 minutes

Final Exam:
Date: May 10, 2026, 7-10 PM
Location: TBD
Topics: Cumulative, with emphasis on:
- Type inference and unification
- Interpreters and closures
- Lambda calculus
- Memory management
Format: Written exam, 3 hours

Study Tips:
- Review all MPs thoroughly
- Practice writing OCaml by hand
- Understand the theory behind implementations
- Work through past exams (available on course website)
"""
            }
        ]
    }
]


# ============================================
# Embedding Functions
# ============================================

def create_deterministic_embedding(text: str) -> List[float]:
    """
    Create a deterministic fake embedding based on text hash.
    This allows vector search to work logically even without real embeddings.
    Similar texts will have somewhat similar (but not identical) embeddings.
    """
    # Create a hash of the text
    text_hash = hashlib.sha256(text.encode()).hexdigest()
    
    # Use the hash to seed a deterministic sequence
    embedding = []
    for i in range(EMBEDDING_DIM):
        # Take 4 characters of hash, cycle through
        hex_chunk = text_hash[(i * 4) % len(text_hash):((i * 4) % len(text_hash)) + 4]
        if len(hex_chunk) < 4:
            hex_chunk = text_hash[:4]
        
        # Convert to float between -1 and 1
        val = (int(hex_chunk, 16) / 65535) * 2 - 1
        embedding.append(val)
    
    # Normalize the embedding
    magnitude = sum(x ** 2 for x in embedding) ** 0.5
    if magnitude > 0:
        embedding = [x / magnitude for x in embedding]
    
    return embedding


def create_openai_embedding(text: str, client) -> List[float]:
    """Create embedding using OpenAI API."""
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding


def get_embedding(text: str, openai_client=None) -> List[float]:
    """Get embedding for text, using OpenAI if available, otherwise deterministic."""
    if openai_client:
        try:
            return create_openai_embedding(text, openai_client)
        except Exception as e:
            print(f"  Warning: OpenAI embedding failed ({e}), using deterministic")
            return create_deterministic_embedding(text)
    return create_deterministic_embedding(text)


# ============================================
# Text Chunking
# ============================================

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into overlapping chunks.
    Tries to break at sentence boundaries when possible.
    """
    # Clean up text
    text = text.strip()
    if not text:
        return []
    
    chunks = []
    start = 0
    
    while start < len(text):
        # Get chunk
        end = start + chunk_size
        
        if end >= len(text):
            chunks.append(text[start:].strip())
            break
        
        # Try to break at sentence boundary
        chunk = text[start:end]
        
        # Look for last sentence-ending punctuation
        last_period = max(
            chunk.rfind('. '),
            chunk.rfind('! '),
            chunk.rfind('? '),
            chunk.rfind('\n\n')
        )
        
        if last_period > chunk_size // 2:
            end = start + last_period + 1
        
        chunks.append(text[start:end].strip())
        start = end - overlap
    
    return [c for c in chunks if len(c) > 50]  # Filter out tiny chunks


# ============================================
# Database Operations
# ============================================

def clear_rag_tables(supabase: Client):
    """Clear existing RAG data."""
    print("Clearing existing RAG data...")
    # Delete in order due to foreign keys
    supabase.table('course_chunks').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
    supabase.table('course_documents').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
    supabase.table('rag_courses').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
    print("  Done!")


def insert_course(supabase: Client, code: str, name: str) -> str:
    """Insert a course and return its ID."""
    result = supabase.table('rag_courses').insert({
        'code': code,
        'name': name
    }).execute()
    return result.data[0]['id']


def insert_document(supabase: Client, course_id: str, title: str, source: str, content: str) -> str:
    """Insert a document and return its ID."""
    result = supabase.table('course_documents').insert({
        'course_id': course_id,
        'title': title,
        'source': source,
        'content': content
    }).execute()
    return result.data[0]['id']


def insert_chunks(supabase: Client, chunks_data: List[Dict[str, Any]]):
    """Insert chunks in batches."""
    batch_size = 50
    for i in range(0, len(chunks_data), batch_size):
        batch = chunks_data[i:i + batch_size]
        supabase.table('course_chunks').insert(batch).execute()


# ============================================
# Main Seeding Function
# ============================================

def seed_database():
    """Main function to seed the database with mock data."""
    print("=" * 60)
    print("Classly RAG - Database Seeder")
    print("=" * 60)
    
    # Validate environment
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("\nError: Missing Supabase credentials!")
        print("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in your .env file")
        sys.exit(1)
    
    print(f"\nSupabase URL: {SUPABASE_URL[:40]}...")
    
    # Initialize clients
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    openai_client = None
    if OPENAI_API_KEY:
        try:
            from openai import OpenAI
            openai_client = OpenAI(api_key=OPENAI_API_KEY)
            print("OpenAI client initialized - using real embeddings")
        except ImportError:
            print("Warning: openai package not installed, using deterministic embeddings")
    else:
        print("No OPENAI_API_KEY found - using deterministic embeddings")
    
    # Clear existing data
    clear_rag_tables(supabase)
    
    # Seed courses
    print("\nSeeding courses...")
    total_chunks = 0
    
    for course_data in MOCK_COURSES:
        code = course_data['code']
        name = course_data['name']
        print(f"\n  [{code}] {name}")
        
        # Insert course
        course_id = insert_course(supabase, code, name)
        print(f"    Course ID: {course_id}")
        
        # Process documents
        for doc in course_data['documents']:
            title = doc['title']
            source = doc['source']
            content = doc['content']
            
            # Insert document
            doc_id = insert_document(supabase, course_id, title, source, content)
            print(f"    Document: {title}")
            
            # Chunk the document
            chunks = chunk_text(content)
            print(f"      Chunks: {len(chunks)}")
            
            # Create embeddings and prepare for insertion
            chunks_data = []
            for idx, chunk_content in enumerate(chunks):
                embedding = get_embedding(chunk_content, openai_client)
                
                chunks_data.append({
                    'course_id': course_id,
                    'doc_id': doc_id,
                    'chunk_index': idx,
                    'content': chunk_content,
                    'embedding': embedding,
                    'metadata': {
                        'doc_title': title,
                        'source': source,
                        'chunk_index': idx,
                        'total_chunks': len(chunks)
                    }
                })
            
            # Insert chunks
            insert_chunks(supabase, chunks_data)
            total_chunks += len(chunks)
    
    print("\n" + "=" * 60)
    print("Seeding Complete!")
    print(f"  Courses: {len(MOCK_COURSES)}")
    print(f"  Documents: {sum(len(c['documents']) for c in MOCK_COURSES)}")
    print(f"  Chunks: {total_chunks}")
    print("=" * 60)


if __name__ == '__main__':
    seed_database()
