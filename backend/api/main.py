"""
FastAPI application for Sapiens MVP.

Provides REST API endpoints for the multi-agent system.
"""

import os
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import structlog

from ..orchestration.orchestrator import Orchestrator
from ..modules.rag import RAGModule
from ..modules.logging import LoggingModule

logger = structlog.get_logger()

# Global orchestrator instance
orchestrator: Optional[Orchestrator] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup orchestrator."""

    global orchestrator

    # Initialize modules
    rag_module = RAGModule(
        persist_dir=os.getenv("CHROMA_PERSIST_DIR", "./data/chroma"),
        embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    )

    logging_module = LoggingModule(
        storage_dir=os.getenv("LOG_STORAGE_DIR", "./data/logs")
    )

    # Initialize orchestrator
    orchestrator = Orchestrator(
        rag_module=rag_module,
        logging_module=logging_module,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    logger.info("Application started")

    yield

    # Cleanup
    logger.info("Application shutdown")


# Create FastAPI app
app = FastAPI(
    title="Sapiens MVP API",
    description="Multi-agent system for project-based career guidance",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Request/Response Models
# ============================================================================

class ChatRequest(BaseModel):
    """Request to send a message."""

    user_id: str
    message: str
    room_id: Optional[str] = None  # Room ID for conversation separation


class ChatResponse(BaseModel):
    """Response from chat."""

    user_id: str
    response: str
    current_state: str


class UserStateResponse(BaseModel):
    """User state response."""

    user_id: str
    current_state: str
    state_entered_at: str
    context: dict


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint."""

    return HealthResponse(
        status="healthy",
        version="0.1.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""

    return HealthResponse(
        status="healthy",
        version="0.1.0"
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint.

    Send a message to the system and get a response.
    """

    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")

    try:
        # Debug logging
        logger.info(
            "chat_request_received",
            user_id=request.user_id,
            room_id=request.room_id,
            has_room_id=request.room_id is not None
        )

        # Process message
        response = orchestrator.process_user_message(
            user_id=request.user_id,
            message=request.message,
            room_id=request.room_id
        )

        # Get updated state (use room_id if provided)
        state_key = f"{request.user_id}_{request.room_id}" if request.room_id else request.user_id
        user_state = orchestrator.logging_module.load_user_state(state_key)

        return ChatResponse(
            user_id=request.user_id,
            response=response,
            current_state=user_state.current_state if user_state else "unknown"
        )

    except Exception as e:
        logger.error("Chat error", user_id=request.user_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@app.get("/api/state/{user_id}", response_model=UserStateResponse)
async def get_state(user_id: str):
    """
    Get user's current state.
    """

    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")

    try:
        user_state = orchestrator.logging_module.load_user_state(user_id)

        if not user_state:
            raise HTTPException(status_code=404, detail="User not found")

        return UserStateResponse(
            user_id=user_state.user_id,
            current_state=user_state.current_state,
            state_entered_at=user_state.state_entered_at.isoformat(),
            context=user_state.context
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Get state error", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Error getting state: {str(e)}")


@app.get("/api/project/{user_id}")
async def get_project(user_id: str):
    """
    Get user's project details.
    """

    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")

    try:
        user_state = orchestrator.logging_module.load_user_state(user_id)

        if not user_state or not user_state.project_id:
            raise HTTPException(status_code=404, detail="Project not found")

        project = orchestrator.logging_module.load_project(
            user_id,
            user_state.project_id
        )

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        return project.model_dump()

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Get project error", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Error getting project: {str(e)}")


@app.get("/api/conversation/{user_id}")
async def get_conversation(user_id: str, limit: Optional[int] = 50):
    """
    Get conversation history.
    """

    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")

    try:
        history = orchestrator.logging_module.get_conversation_history(
            user_id,
            limit=limit
        )

        return {"user_id": user_id, "history": history}

    except Exception as e:
        logger.error("Get conversation error", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Error getting conversation: {str(e)}")


@app.post("/api/users")
async def create_user(user_id: str):
    """
    Create a new user.
    """

    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")

    try:
        # Check if user exists
        existing_state = orchestrator.logging_module.load_user_state(user_id)

        if existing_state:
            return {"user_id": user_id, "status": "exists"}

        # Create new user state
        from ..schemas.state import UserState, StateType

        user_state = UserState(
            user_id=user_id,
            current_state=StateType.ONBOARDING
        )

        orchestrator.logging_module.save_user_state(user_state)

        return {"user_id": user_id, "status": "created"}

    except Exception as e:
        logger.error("Create user error", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""

    logger.error("Unhandled exception", path=request.url.path, error=str(exc))

    return {
        "detail": "An internal error occurred. Please try again.",
        "type": type(exc).__name__
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
