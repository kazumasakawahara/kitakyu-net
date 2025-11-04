# -*- coding: utf-8 -*-
"""
FastAPI backend for facility search assistant.

This module provides REST API endpoints for:
- Natural language facility search
- Health checks
- Statistics
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from loguru import logger

from backend.llm.rag_pipeline import get_rag_pipeline
from backend.neo4j.client import get_neo4j_client
from backend.api.routes import users, assessments, goals, service_needs, documents, plans, monitoring

# Initialize FastAPI app
app = FastAPI(
    title="Kitakyu Facility Search API",
    description="AI-powered facility search for Kitakyushu disability welfare services",
    version="1.0.0",
)

# Include routers
app.include_router(users.router, prefix="/api")
app.include_router(assessments.router, prefix="/api")
app.include_router(plans.router, prefix="/api")
app.include_router(goals.router, prefix="/api")
app.include_router(service_needs.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(monitoring.router, prefix="/api")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class SearchRequest(BaseModel):
    """Search request model."""

    query: str
    limit: Optional[int] = 20


class SearchResponse(BaseModel):
    """Search response model."""

    query: str
    answer: str
    facilities: List[Dict[str, Any]]
    facility_count: int
    search_params: Dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    neo4j_connected: bool
    ollama_available: bool


class StatsResponse(BaseModel):
    """Statistics response."""

    total_facilities: int
    by_service_type: Dict[str, int]
    by_district: Dict[str, int]


# API endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "Kitakyu Facility Search API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    logger.info("Health check requested")

    # Check Neo4j connection
    neo4j_ok = False
    try:
        client = get_neo4j_client()
        client.get_facility_count()
        neo4j_ok = True
    except Exception as e:
        logger.error(f"Neo4j health check failed: {e}")

    # Check Ollama availability
    ollama_ok = False
    try:
        from backend.llm.ollama_client import get_ollama_client

        ollama = get_ollama_client()
        ollama_ok = ollama.check_availability()
    except Exception as e:
        logger.error(f"Ollama health check failed: {e}")

    status = "healthy" if (neo4j_ok and ollama_ok) else "unhealthy"

    return HealthResponse(
        status=status, neo4j_connected=neo4j_ok, ollama_available=ollama_ok
    )


@app.post("/search", response_model=SearchResponse)
async def search_facilities(request: SearchRequest):
    """
    Search facilities using natural language query.

    Args:
        request: SearchRequest with query string

    Returns:
        SearchResponse with answer and facilities
    """
    logger.info(f"Search request: {request.query}")

    try:
        # Execute RAG search
        pipeline = get_rag_pipeline()
        result = pipeline.search(request.query)

        return SearchResponse(
            query=result["query"],
            answer=result["answer"],
            facilities=result["facilities"],
            facility_count=result["facility_count"],
            search_params=result["search_params"],
        )

    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/stats", response_model=StatsResponse)
async def get_statistics():
    """Get database statistics."""
    logger.info("Statistics requested")

    try:
        client = get_neo4j_client()
        stats = client.get_statistics()

        return StatsResponse(
            total_facilities=stats["total_facilities"],
            by_service_type=stats["by_service_type"],
            by_district=stats["by_district"],
        )

    except Exception as e:
        logger.error(f"Statistics retrieval failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Statistics retrieval failed: {str(e)}"
        )


@app.get("/facilities", response_model=List[Dict[str, Any]])
async def list_facilities(
    limit: int = 20,
    service_type: Optional[str] = None,
    district: Optional[str] = None,
):
    """
    List facilities with optional filters.

    Args:
        limit: Maximum number of facilities to return
        service_type: Filter by service type
        district: Filter by district

    Returns:
        List of facilities
    """
    logger.info(
        f"List facilities: limit={limit}, service_type={service_type}, district={district}"
    )

    try:
        client = get_neo4j_client()
        facilities = client.search_facilities(
            service_type=service_type, district=district, limit=limit
        )

        return facilities

    except Exception as e:
        logger.error(f"Facility listing failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Facility listing failed: {str(e)}"
        )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("=" * 60)
    logger.info("Starting Kitakyu Facility Search API")
    logger.info("=" * 60)

    # Initialize connections
    try:
        neo4j_client = get_neo4j_client()
        count = neo4j_client.get_facility_count()
        logger.success(f"Neo4j connected ({count} facilities)")
    except Exception as e:
        logger.error(f"Neo4j connection failed: {e}")

    try:
        from backend.llm.ollama_client import get_ollama_client

        ollama = get_ollama_client()
        if ollama.check_availability():
            logger.success(f"Ollama connected (model: {ollama.model})")
        else:
            logger.warning("Ollama server not available")
    except Exception as e:
        logger.error(f"Ollama connection failed: {e}")

    logger.info("=" * 60)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Kitakyu Facility Search API")
