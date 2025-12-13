# Todo App - Phase 3

This is a modern todo application with AI integration, built using Next.js for the frontend and FastAPI for the backend.

## Project Structure

```
/backend          # FastAPI application
/frontend         # Next.js application
/specs            # Specification files
```

## Backend Setup

The backend is built with FastAPI and includes:

- Virtual environment (`venv`)
- Dependencies in `requirements.txt`
- Basic application structure in `main.py`

### Installation

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running the Backend

```bash
cd backend
uvicorn main:app --reload
```

## Frontend Setup

The frontend is built with Next.js and includes:

- Tailwind CSS for styling
- Basic app structure with Next.js 16+
- Ready for OpenAI ChatKit integration

### Installation

```bash
cd frontend
npm install
```

### Running the Frontend

```bash
cd frontend
npm run dev
```

## Tech Stack

- **Frontend**: Next.js 16+, OpenAI ChatKit, Tailwind CSS
- **Backend**: Python FastAPI, OpenAI Agents SDK, Official MCP SDK
- **Database**: Neon Serverless PostgreSQL (SQLModel)
- **Auth**: Better Auth (JWT)