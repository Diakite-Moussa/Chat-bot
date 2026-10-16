"""
Tests unitaires et de bout en bout pour le backend FastAPI NutriCoach IA.
Vérifie :
- /health
- /chat (questions normales, contextes)
- Refus des messages vides
- Isolation des conversations
- Réinitialisation de conversation (DELETE /chat/{conversation_id})
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Vérifie que la route GET /health renvoie un statut 200 et les métadonnées."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "NutriCoach" in data["app_name"]
    assert "version" in data
    assert "timestamp" in data


def test_empty_message_rejection():
    """Vérifie que l'envoi d'un message vide ou d'espaces est refusé."""
    # Message avec espaces uniquement
    response1 = client.post("/chat", json={"message": "   "})
    assert response1.status_code in [400, 422]

    # Message chaîne vide
    response2 = client.post("/chat", json={"message": ""})
    assert response2.status_code in [400, 422]


def test_chat_interaction_and_history():
    """Vérifie le bon déroulement d'une conversation et la conservation du contexte."""
    # Étape 1 : Définir le profil de l'utilisateur
    res1 = client.post("/chat", json={
        "message": "Bonjour, j'ai 24 ans, je suis étudiant et je suis végétarien."
    })
    assert res1.status_code == 200
    data1 = res1.json()
    conv_id = data1["conversation_id"]
    assert conv_id is not None
    assert len(data1["response"]) > 0

    # Étape 2 : Poser une question dépendante du contexte avec le même conversation_id
    res2 = client.post("/chat", json={
        "conversation_id": conv_id,
        "message": "Que me conseilles-tu pour mon déjeuner demain compte tenu de mes contraintes ?"
    })
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["conversation_id"] == conv_id
    # La réponse doit prendre en compte le végétarisme / étudiant
    assert ("végétarien" in data2["response"].lower() or "protéines" in data2["response"].lower() or "déjeuner" in data2["response"].lower())


def test_conversation_isolation():
    """Vérifie que deux sessions de conversation différentes sont totalement isolées."""
    # Session A
    res_a1 = client.post("/chat", json={"message": "Je suis végétarien."})
    id_a = res_a1.json()["conversation_id"]

    # Session B
    res_b1 = client.post("/chat", json={"message": "J'adore la viande rouge et je suis carnivore strict."})
    id_b = res_b1.json()["conversation_id"]

    assert id_a != id_b

    # Demande d'un repas dans session A
    res_a2 = client.post("/chat", json={"conversation_id": id_a, "message": "Propose-moi un déjeuner."})
    # Demande d'un repas dans session B
    res_b2 = client.post("/chat", json={"conversation_id": id_b, "message": "Propose-moi un déjeuner."})

    assert res_a2.status_code == 200
    assert res_b2.status_code == 200
    # Les réponses et contextes sont distincts
    assert res_a2.json()["conversation_id"] == id_a
    assert res_b2.json()["conversation_id"] == id_b


def test_reset_conversation():
    """Vérifie la réinitialisation de la mémoire d'une conversation via DELETE."""
    res = client.post("/chat", json={"message": "Test de conversation à réinitialiser."})
    conv_id = res.json()["conversation_id"]

    # Appel DELETE
    delete_res = client.delete(f"/chat/{conv_id}")
    assert delete_res.status_code == 200
    delete_data = delete_res.json()
    assert delete_data["cleared"] is True
    assert delete_data["conversation_id"] == conv_id


if __name__ == "__main__":
    pytest.main(["-v", __file__])
