# DELTA Architecture Refactor (Jan 2026)

This document describes the architectural patterns established during the recent refactoring of the DELTA platform.

## Backend: Service-Router-Dependency Pattern

The backend has transitioned from singleton-based service access to a modern **Dependency Injection (DI)** pattern leveraging FastAPI's `Depends` utility.

### 1. Layers
- **Models (`models.py`)**: SQLAlchemy definitions for the database schema.
- **Schemas (`schemas.py`)**: Pydantic models for request/response validation and type safety.
- **Services (`api/services/`)**: Business logic layer. Services handle data processing, external API calls (e.g., Vertex AI), and complex database operations.
- **Routers (`api/routers/`)**: HTTP interface layer. Routers handle endpoint definitions, status codes, and delegate logic to services via DI.
- **Auth (`api/auth.py`)**: Centralized JWT and password security logic.

### 2. Dependency Injection
Services are now injected into routers using `Depends`. This enables:
- **Testability**: Services can be easily mocked in unit tests.
- **Clean Code**: Routers remain "thin," focusing only on HTTP concerns.
- **Modularity**: Services can depend on other services through constructor injection.

Example:
```python
@router.post("/process")
async def process_input(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
    current_user: User = Depends(get_current_user)
):
    return await chat_service.process_user_input(...)
```

### 3. Background Job Tracking
Stalled modeling jobs (e.g., those left in `RUNNING` status after a server crash) are automatically detected and marked as `STALLED` during the application startup lifespan.

---

## Frontend: TypeScript & Domain-Driven API

The frontend has moved toward a more robust, type-safe architecture.

### 1. TypeScript Migration
Core modules have been converted to TypeScript (`.ts`/`.tsx`):
- **API Client**: `api/client.ts` provides a type-safe wrapper around `fetch` with automatic retry logic and JWT injection.
- **Contexts**: `ConversationContext.tsx` provides full type safety for the application's global state and chat flows.

### 2. Domain-Driven API Modules
API calls are now grouped by domain rather than being monolithic:
- `api/media.ts`: TTS and Image generation.
- `api/modeling.ts`: Simulation job submission and tracking.
- `api/auth.ts`: Authentication and token management.

### 3. Error Handling
The frontend now utilizes robust error propagation. API errors are thrown as `ApiError` objects, allowing UI components or hooks to provide meaningful feedback (e.g., error toasts) instead of failing silently.
