"""
Pramana AI Strict-RAG Backend API.
Entrypoint for Bali DigiFest 2026 AI Web Innovation Challenge.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.models.schemas import (
    TripBriefRequest,
    TripBriefResponse,
    ContextNoteRequest,
    ContextNoteResponse,
    CorpusResponse
)
from backend.services.rag_engine import StrictRAGEngine
from backend.services.corpus_loader import CorpusManager

app = FastAPI(
    title="Pramana Strict-RAG API",
    version="1.0.0",
    description="High-assurance legal intelligence and compliance platform for Bali tourism."
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_engine = StrictRAGEngine()
corpus_manager = CorpusManager.get_instance()


@app.get("/api/v1/health")
def healthcheck():
    return {
        "status": "healthy",
        "service": "pramana-strict-rag",
        "version": "1.0.0",
        "total_regulations_indexed": len(corpus_manager.get_all())
    }


@app.get("/api/v1/corpus", response_model=CorpusResponse)
def get_corpus():
    """Returns active registered regulations and legal tier metadata for UI transparency."""
    return {
        "metadata": corpus_manager.metadata,
        "tiers": corpus_manager.tiers,
        "regulations": corpus_manager.get_all()
    }


@app.post("/api/v1/trip-brief", response_model=TripBriefResponse)
def generate_trip_brief(req: TripBriefRequest):
    """
    Mode 1: Generate itinerary-based compliance briefing.
    Detects Nyepi conflicts, extracts relevant statutes, and formats WhatsApp / ICS outputs.
    """
    try:
        result = rag_engine.analyze_trip_itinerary(
            itinerary_text=req.itinerary_text,
            start_date=req.start_date,
            end_date=req.end_date,
            traveler_origin=req.traveler_origin
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memproses trip brief: {str(e)}")


@app.post("/api/v1/context-note", response_model=ContextNoteResponse)
def generate_context_note(req: ContextNoteRequest):
    """
    Mode 2: Generate neutral, verifiable Context Note for viral tourism content.
    Identifies legal grounds, emotional framing, and returns exact statute citations.
    """
    try:
        result = rag_engine.analyze_viral_post(post_content=req.post_content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memproses catatan konteks: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
