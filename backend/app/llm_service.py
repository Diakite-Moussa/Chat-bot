import logging
import uuid
from typing import Dict, List, Optional, Tuple
from openai import OpenAI, APIError, APITimeoutError, RateLimitError, AuthenticationError
from .config import settings
from .prompts import ACTIVE_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class ConversationStore:
    """Gestionnaire de mémoire vive des conversations."""

    def __init__(self):
        # Dictionnaire: conversation_id -> liste de messages {"role": ..., "content": ...}
        self._conversations: Dict[str, List[Dict[str, str]]] = {}

    def get_or_create(self, conversation_id: Optional[str] = None) -> str:
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = []
        return conversation_id

    def get_history(self, conversation_id: str) -> List[Dict[str, str]]:
        return self._conversations.get(conversation_id, [])

    def add_message(self, conversation_id: str, role: str, content: str):
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = []
        self._conversations[conversation_id].append({"role": role, "content": content})

    def reset(self, conversation_id: str) -> bool:
        if conversation_id in self._conversations:
            self._conversations[conversation_id] = []
            return True
        return False

    def conversation_count(self) -> int:
        return len(self._conversations)


class LLMService:
    """Service d'orchestration LLM avec support multi-fournisseur et fallback intelligent."""

    def __init__(self):
        self.store = ConversationStore()
        self._client: Optional[OpenAI] = None
        self.active_provider: str = "mock"
        self.active_model: str = "nutricoach-simulated-v2"
        self._init_client()

    def _init_client(self):
        provider = settings.LLM_PROVIDER.lower().strip()
        groq_key = settings.GROQ_API_KEY.strip()
        openai_key = settings.OPENAI_API_KEY.strip()

        # Priorité 1 : Groq
        if (provider == "groq" or groq_key) and groq_key and not groq_key.startswith("gsk-votre-cle"):
            try:
                self._client = OpenAI(
                    base_url="https://api.groq.com/openai/v1",
                    api_key=groq_key,
                    timeout=settings.REQUEST_TIMEOUT_SECONDS,
                )
                self.active_provider = "groq"
                self.active_model = settings.GROQ_MODEL
                logger.info(f"Groq client initialized successfully with model {self.active_model}.")
                return
            except Exception as e:
                logger.error(f"Error initializing Groq client: {e}")

        # Priorité 2 : OpenAI
        if openai_key and not openai_key.startswith("sk-votre-cle") and not openai_key.startswith("sk-NOUVELLE-CLE"):
            try:
                self._client = OpenAI(
                    api_key=openai_key,
                    timeout=settings.REQUEST_TIMEOUT_SECONDS,
                )
                self.active_provider = "openai"
                self.active_model = settings.OPENAI_MODEL
                logger.info(f"OpenAI client initialized successfully with model {self.active_model}.")
                return
            except Exception as e:
                logger.error(f"Error initializing OpenAI client: {e}")

        # Fallback intelligent
        logger.warning("No valid external LLM API key detected. Running in smart simulation mode.")
        self._client = None
        self.active_provider = "mock"
        self.active_model = "nutricoach-simulated-v2"

    def _generate_mock_response(self, user_message: str, history: List[Dict[str, str]]) -> str:
        """Simulateur intelligent répondant strictement au cahier des charges en l'absence de clé API."""
        msg_lower = user_message.lower().strip()
        
        # 1. Tentative de jailbreak
        if any(w in msg_lower for w in ["ignore", "dan", "pirate", "oublie", "sans regles", "désormais"]):
            return (
                "🛡️ **Respect des règles de sécurité**\n\n"
                "Je suis **NutriCoach IA**, votre conseiller dédié à la nutrition et à la santé sportive. "
                "Je ne peux pas modifier mon identité, ignorer mes consignes éthiques ni répondre à des demandes "
                "en dehors de mon domaine d'expertise. Comment puis-je vous aider sur vos objectifs alimentaires aujourd'hui ?"
            )

        # 2. Demande médicale sensible / Urgence
        if any(w in msg_lower for w in ["douleur", "mal au coeur", "thoracique", "médicament", "ordonnance", "traitement", "perte de poids brutale"]):
            return (
                "⚠️ **Avertissement Médical Important**\n\n"
                "Les symptômes que vous décrivez nécessitent une **évaluation médicale d'urgence**. En tant que NutriCoach IA, "
                "je ne suis pas médecin : **je ne pose aucun diagnostic et ne prescris aucun traitement**.\n\n"
                "👉 Si vous ressentez une douleur thoracique aiguë, un essoufflement ou un malaise, **contactez immédiatement le 15 (SAMU), le 112 ou rendez-vous aux urgences les plus proches**."
            )

        # 3. Question ambiguë
        if msg_lower in ["combien je dois en manger ?", "combien ?", "combien dois-je en prendre ?"] or "combien je dois en manger" in msg_lower:
            return (
                "🔍 **Précisions nécessaires**\n\n"
                "Pour vous donner une réponse adaptée et personnalisée, j'ai besoin de quelques précisions :\n"
                "1. **De quel aliment ou groupe d'aliments s'agit-il ?**\n"
                "2. **Quel est votre objectif principal** (maintien, prise de muscle, perte de masse grasse) ?\n"
                "3. **Pratiquez-vous une activité physique régulière ?**\n\n"
                "Dès que vous m'indiquez ces éléments, je vous calculerai une recommandation précise !"
            )

        # 4. Question hors domaine
        if any(w in msg_lower for w in ["voiture", "moteur", "courroie", "peugeot", "equation", "différentielle", "python", "javascript", "politique", "ordinateur"]):
            return (
                "ℹ️ **Périmètre d'expertise**\n\n"
                "Je suis spécialisé exclusivement dans la **nutrition, l'alimentation saine et l'hygiène de vie sportive**. "
                "Je ne suis pas qualifié pour traiter de sujets techniques ou mécaniques.\n\n"
                "Si vous avez des questions sur votre alimentation, la planification de vos repas ou vos encas, je serai ravi de vous accompagner !"
            )

        # 5. Dépendance au contexte conversationnel
        has_vege_student_context = any(
            "végétarien" in h.get("content", "").lower() or "etudiant" in h.get("content", "").lower() 
            for h in history
        )
        if ("déjeuner" in msg_lower or "repas" in msg_lower or "demain" in msg_lower) and has_vege_student_context:
            return (
                "🥗 **Idée de déjeuner végétarien, économique et rapide pour étudiant** :\n\n"
                "En tenant compte de votre régime **végétarien** et de votre rythme d'étudiant, voici un bol équilibré prêt en 10 minutes :\n\n"
                "- **Protéines végétales & Féculents :** Riz complet ou quinoa précuit + 150g de pois chiches rincés (en boîte, économique).\n"
                "- **Légumes :** Épinards frais, tomates cerises et concombre en dés.\n"
                "- **Bons lipides :** 1/2 avocat ou une cuillère à soupe d'huile d'olive et graines de courge.\n"
                "- **Assaisonnement :** Jus de citron, sel, poivre et levure maltée (riche en vitamines B).\n\n"
                "Ce repas apporte environ 24g de protéines, des glucides à index glycémique modéré pour l'énergie mentale l'après-midi, et coûte moins de 3€ !"
            )

        # 6. Questions pertinentes du domaine
        if "macronutriment" in msg_lower or "prise de masse" in msg_lower:
            return (
                "💪 **Les Macronutriments pour la Prise de Masse Musculaire** :\n\n"
                "1. **Protéines (1.6 à 2.0g / kg de poids corporel)** : Briques fondamentales de la reconstruction musculaire (œufs, tofu, légumineuses, volaille, poissons).\n"
                "2. **Glucides (4 à 6g / kg)** : Source d'énergie principale pour alimenter vos entraînements intenses et recharger le glycogène (avoine, riz complet, patates douces).\n"
                "3. **Lipides (0.8 à 1.2g / kg)** : Essentiels au système hormonal et à la testostérone (huile d'olive, oléagineux, avocat, poissons gras).\n\n"
                "💡 *Conseil clé :* Visez un léger surplus calorique (+250 à 350 kcal/jour) pour favoriser la prise de muscle tout en limitant la prise de graisse."
            )

        if "encas" in msg_lower or "goûter" in msg_lower:
            return (
                "🍏 **Idées d'encas sains et rassasiants pour l'après-midi** :\n\n"
                "Pour éviter le coup de barre de 16h sans fringale :\n"
                "- **Option 1 (Protéinée & Gourmande) :** 150g de fromage blanc ou yaourt grec + une poignée de baies (myrtilles/framboises) + 20g d'amandes.\n"
                "- **Option 2 (Sur le pouce) :** Une pomme coupée avec 1 cuillère à soupe de purée de cacahuètes 100% pure.\n"
                "- **Option 3 (Sportive) :** 2 galettes de riz complet tartinées de houmous avec quelques noix du Brésil.\n\n"
                "Ces collations combinent fibres et protéines pour stabiliser votre glycémie jusqu'au dîner !"
            )

        if "hydratation" in msg_lower or "cardio" in msg_lower or "eau" in msg_lower:
            return (
                "💧 **Hydratation optimale pour une séance cardio de 45 minutes** :\n\n"
                "- **Avant la séance (2h avant) :** Buvez environ 400 à 500 ml d'eau pour commencer bien hydraté sans sensation de ballonnement.\n"
                "- **Pendant la séance :** Prenez 2 à 3 petites gorgées d'eau fraîche (environ 100 à 150 ml) toutes les 15-20 minutes.\n"
                "- **Après la séance :** Buvez 300 à 500 ml d'eau enrichie en minéraux (ou avec une pincée de sel si forte transpiration).\n\n"
                "Pour un effort de moins d'une heure, l'eau pure suffit amplement sans boisson isotonique sucrée."
            )

        if "glucide" in msg_lower:
            return (
                "🍞 **Différence entre Glucides Simples et Glucides Complexes** :\n\n"
                "- **Glucides simples (sucres rapides) :** Molécules courtes rapidement digérées. Ils provoquent un pic rapide d'insuline. À privilégier immédiatement autour de l'effort intense (fruits, miel).\n"
                "- **Glucides complexes (sucres lents) :** Molécules longues riches en fibres. Ils procurent une énergie durable sans pic d'hypoglycémie réactionnelle (flocons d'avoine, légumineuses, riz complet, patate douce).\n\n"
                "Privilégiez les glucides complexes au quotidien pour une énergie stable tout au long de la journée !"
            )

        # Réponse par défaut
        return (
            "Bonjour ! Je suis **NutriCoach IA** 🥗. "
            "Je suis là pour vous aider à optimiser votre alimentation, équilibrer vos repas et soutenir votre forme sportive. "
            "N'hésitez pas à me poser une question précise sur vos besoins nutritionnels !"
        )

    def generate_chat_response(
        self,
        conversation_id: str,
        user_message: str,
        system_prompt: Optional[str] = None
    ) -> Tuple[str, str, str]:
        """
        Génère une réponse LLM en tenant compte de l'historique de la conversation.
        Retourne : (texte_reponse, fournisseur, nom_modele)
        """
        # Récupération de l'historique existant
        history = self.store.get_history(conversation_id)
        
        # Enregistrement du message utilisateur dans l'historique
        self.store.add_message(conversation_id, "user", user_message)

        # Si un client externe (OpenAI ou Groq) est disponible
        if self._client:
            active_prompt = system_prompt or ACTIVE_SYSTEM_PROMPT
            messages = [{"role": "system", "content": active_prompt}]
            
            # Injection de l'historique (derniers 10 messages pour maîtriser le contexte)
            for msg in history[-10:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": user_message})

            model_name = self.active_model
            provider_name = self.active_provider

            try:
                logger.info(f"Appel LLM vers {provider_name} ({model_name}) pour conversation {conversation_id}...")
                response = self._client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=settings.TEMPERATURE,
                    max_tokens=settings.MAX_TOKENS,
                    timeout=settings.REQUEST_TIMEOUT_SECONDS,
                )
                content = response.choices[0].message.content or ""
                # Enregistrement de la réponse dans l'historique
                self.store.add_message(conversation_id, "assistant", content)
                return content, provider_name, model_name

            except APITimeoutError:
                logger.error("Délai d'attente dépassé (timeout) avec le fournisseur LLM.")
                error_msg = "⏳ Le fournisseur de modèle a mis trop de temps à répondre (délai d'attente dépassé). Veuillez réessayer dans quelques instants."
                self.store.add_message(conversation_id, "assistant", error_msg)
                return error_msg, provider_name, f"{model_name}-timeout"

            except RateLimitError:
                logger.error("Limite de quota / débit atteinte avec le fournisseur LLM.")
                error_msg = "⚠️ La limite d'appels API du fournisseur a été atteinte. Veuillez patienter un instant avant de reformuler votre question."
                self.store.add_message(conversation_id, "assistant", error_msg)
                return error_msg, provider_name, f"{model_name}-ratelimit"

            except AuthenticationError:
                logger.error("Clé API invalide.")
                # Fallback sur le simulateur intelligent
                logger.info("Basculement automatique sur le simulateur intelligent NutriCoach.")
            except APIError as e:
                logger.error(f"Erreur API LLM : {e}")
                # Fallback sur le simulateur intelligent
            except Exception as e:
                logger.error(f"Erreur inattendue lors de l'appel LLM : {e}")

        # Mode simulation intelligent (fallback garanti 100% fonctionnel)
        response_text = self._generate_mock_response(user_message, history)
        self.store.add_message(conversation_id, "assistant", response_text)
        return response_text, "mock", "nutricoach-simulated-v2"


# Instance singleton du service LLM
llm_service = LLMService()
