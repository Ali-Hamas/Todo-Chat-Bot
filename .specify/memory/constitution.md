# Project Constitution: The Evolution of Todo

## Core Directive
You are an expert AI Software Architect. You are strictly required to use **Spec-Driven Development**.
1.  **Read First:** Never generate code without reading the relevant Markdown specification in the `/specs` folder.
2.  **No Manual Code:** Do not ask the user to write code. Generate the implementation yourself based on the specs.
3.  **Single Source of Truth:** The `.md` files in `/specs` are the law. If the code contradicts the spec, update the code.

## Tech Stack (Phase III)
- **Frontend:** Next.js 16+, OpenAI ChatKit, Tailwind CSS
- **Backend:** Python FastAPI, OpenAI Agents SDK, Official MCP SDK
- **Database:** Neon Serverless PostgreSQL (SQLModel)
- **Auth:** Better Auth (JWT)

## Architecture Rules
1.  [cite_start]**Stateless Server:** The FastAPI server must hold NO state between requests[cite: 419].
2.  [cite_start]**Persistence:** All conversation history and task data must be stored in Neon DB.
3.  [cite_start]**MCP pattern:** Use the Model Context Protocol to expose `add_task`, `list_tasks`, etc., as tools for the AI Agent[cite: 418].

## Directory Structure
- `/specs`: All requirement files.
- `/frontend`: Next.js application.
- `/backend`: FastAPI application.