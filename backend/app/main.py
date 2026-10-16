import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .models import ChatRequest, ChatResponse, HealthResponse, ResetResponse
from .llm_service import llm_service

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("nutricoach_api")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API FastAPI pour le Chatbot spécialisé en nutrition et bien-être sportif (NutriCoach IA)",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS pour permettre les requêtes depuis React
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": f"Bienvenue sur l'API {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """
    Vérifie l'état de fonctionnement du service backend.
    """
    return HealthResponse(
        status="ok",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        llm_provider=settings.LLM_PROVIDER,
        model=settings.OPENAI_MODEL if settings.LLM_PROVIDER == "openai" else settings.GROQ_MODEL,
        timestamp=datetime.utcnow()
    )


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
def chat(request: ChatRequest):
    """
    Envoie un message au chatbot et reçoit une réponse contextuelle.
    Valide les données avec Pydantic et refuse les messages vides.
    """
    # Validation du message
    cleaned_message = request.message.strip()
    if not cleaned_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le message utilisateur ne peut pas être vide."
        )

    # Récupération ou création de l'identifiant de conversation
    conv_id = llm_service.store.get_or_create(request.conversation_id)

    try:
        response_text, provider, model = llm_service.generate_chat_response(
            conversation_id=conv_id,
            user_message=cleaned_message
        )
        return ChatResponse(
            conversation_id=conv_id,
            response=response_text,
            provider=provider,
            model=model,
            created_at=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Erreur interne lors du traitement du chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne lors de la génération de la réponse : {str(e)}"
        )


@app.delete("/chat/{conversation_id}", response_model=ResetResponse, tags=["Chat"])
def reset_conversation(conversation_id: str):
    """
    Réinitialise l'historique d'une conversation spécifique.
    """
    if not conversation_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'identifiant de la conversation doit être renseigné."
        )

    cleared = llm_service.store.reset(conversation_id)
    return ResetResponse(
        conversation_id=conversation_id,
        message=f"La conversation {conversation_id} a été réinitialisée avec succès." if cleared else "Nouvelle conversation prête.",
        cleared=cleared
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
