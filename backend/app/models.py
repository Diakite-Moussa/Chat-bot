from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ChatMessage(BaseModel):
    role: str = Field(..., description="Rôle de l'émetteur : 'user', 'assistant' ou 'system'")
    content: str = Field(..., description="Contenu textuel du message")
    timestamp: datetime = Field(default_factory=utc_now, description="Horodatage UTC")


class ChatRequest(BaseModel):
    conversation_id: Optional[str] = Field(
        None, 
        description="Identifiant unique de la conversation. Si non fourni, un nouvel ID sera généré."
    )
    message: str = Field(
        ..., 
        min_length=1, 
        max_length=4000, 
        description="Message de l'utilisateur (ne doit pas être vide)"
    )

    @field_validator("message")
    @classmethod
    def validate_message_not_empty(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Le message ne peut pas être vide ou constitué uniquement d'espaces.")
        return trimmed


class ChatResponse(BaseModel):
    conversation_id: str = Field(..., description="Identifiant unique de la conversation")
    response: str = Field(..., description="Réponse générée par le chatbot")
    provider: str = Field(..., description="Fournisseur LLM utilisé (openai, groq, mock)")
    model: str = Field(..., description="Modèle utilisé")
    created_at: datetime = Field(default_factory=utc_now)


class HealthResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "ok"})
    app_name: str
    version: str
    llm_provider: str
    model: str
    timestamp: datetime = Field(default_factory=utc_now)


class ResetResponse(BaseModel):
    conversation_id: str
    message: str
    cleared: bool
