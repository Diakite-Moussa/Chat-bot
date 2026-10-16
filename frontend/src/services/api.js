/**
 * Client API pour communiquer avec le backend FastAPI NutriCoach IA.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) {
      throw new Error(`Statut HTTP non valide: ${res.status}`);
    }
    return await res.json();
  } catch (error) {
    console.warn("Backend /health unreachable:", error);
    return null;
  }
}

export async function sendChatMessage(message, conversationId = null) {
  const trimmed = message ? message.trim() : '';
  if (!trimmed) {
    throw new Error("Le message ne peut pas être vide.");
  }

  const payload = {
    message: trimmed,
  };
  if (conversationId) {
    payload.conversation_id = conversationId;
  }

  try {
    const res = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      let errorDetail = `Erreur ${res.status}`;
      try {
        const errorData = await res.json();
        if (errorData.detail) {
          errorDetail = Array.isArray(errorData.detail)
            ? errorData.detail.map(d => d.msg || d).join(', ')
            : errorData.detail;
        }
      } catch (e) {
        // Ignorer si non JSON
      }
      throw new Error(errorDetail);
    }

    return await res.json();
  } catch (error) {
    // Si fetch a échoué (réseau indisponible / serveur éteint)
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error("Le serveur backend FastAPI est actuellement inaccessible (Vérifiez qu'il tourne sur http://127.0.0.1:8000).");
    }
    throw error;
  }
}

export async function resetConversation(conversationId) {
  if (!conversationId) return { cleared: true };
  try {
    const res = await fetch(`${API_BASE_URL}/chat/${encodeURIComponent(conversationId)}`, {
      method: 'DELETE',
    });
    if (!res.ok) {
      throw new Error(`Impossible de réinitialiser la conversation (${res.status})`);
    }
    return await res.json();
  } catch (error) {
    console.warn("Erreur lors de la réinitialisation:", error);
    return { cleared: true, message: "Réinitialisation locale effectuée." };
  }
}
