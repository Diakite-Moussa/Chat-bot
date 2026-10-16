import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import MessageItem from './components/MessageItem';
import MessageInput from './components/MessageInput';
import WelcomeHero from './components/WelcomeHero';
import DisclaimerModal from './components/DisclaimerModal';
import { checkBackendHealth, sendChatMessage, resetConversation } from './services/api';
import { AlertCircle, X } from 'lucide-react';

export default function App() {
  const [conversationId, setConversationId] = useState(() => {
    return localStorage.getItem('nutricoach_conv_id') || null;
  });
  const [messages, setMessages] = useState(() => {
    const saved = localStorage.getItem('nutricoach_messages');
    return saved ? JSON.parse(saved) : [];
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const [backendStatus, setBackendStatus] = useState({ online: false, provider: null });
  const [isDisclaimerOpen, setIsDisclaimerOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const messagesEndRef = useRef(null);

  // Sauvegarde locale de l'historique de session
  useEffect(() => {
    localStorage.setItem('nutricoach_messages', JSON.stringify(messages));
  }, [messages]);

  useEffect(() => {
    if (conversationId) {
      localStorage.setItem('nutricoach_conv_id', conversationId);
    }
  }, [conversationId]);

  // Vérification de l'état du backend au chargement et périodiquement
  useEffect(() => {
    const pingHealth = async () => {
      const data = await checkBackendHealth();
      if (data && data.status === 'ok') {
        setBackendStatus({
          online: true,
          provider: data.llm_provider,
          model: data.model,
          appName: data.app_name,
        });
      } else {
        setBackendStatus({ online: false, provider: null });
      }
    };

    pingHealth();
    const interval = setInterval(pingHealth, 12000);
    return () => clearInterval(interval);
  }, []);

  // Défilement automatique vers le bas
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Envoi d'un message
  const handleSendMessage = async (userText) => {
    setErrorMessage(null);

    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: userText,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const result = await sendChatMessage(userText, conversationId);
      
      // Mise à jour de l'ID conversationnel
      if (result.conversation_id && result.conversation_id !== conversationId) {
        setConversationId(result.conversation_id);
      }

      const botMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: result.response,
        provider: result.provider ? `${result.provider} (${result.model})` : null,
        timestamp: result.created_at || new Date().toISOString(),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error("Chat error:", err);
      setErrorMessage(err.message || "Une erreur inattendue s'est produite lors de la communication avec l'assistant.");
    } finally {
      setIsLoading(false);
    }
  };

  // Réinitialisation de la conversation
  const handleReset = async () => {
    if (isResetting) return;
    setIsResetting(true);
    setErrorMessage(null);

    try {
      if (conversationId) {
        await resetConversation(conversationId);
      }
    } catch (e) {
      console.warn("Reset error:", e);
    } finally {
      // Génère une nouvelle session vierge
      const newId = 'session_' + Math.random().toString(36).substring(2, 11);
      setConversationId(newId);
      setMessages([]);
      localStorage.removeItem('nutricoach_messages');
      localStorage.removeItem('nutricoach_conv_id');
      setIsResetting(false);
    }
  };

  return (
    <div className="app-container">
      {/* En-tête */}
      <Header
        backendStatus={backendStatus}
        onResetConversation={handleReset}
        onOpenDisclaimer={() => setIsDisclaimerOpen(true)}
        isResetting={isResetting}
      />

      {/* Bannière d'erreur éventuelle */}
      {errorMessage && (
        <div className="error-banner" id="error-banner">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertCircle size={18} />
            <span>{errorMessage}</span>
          </div>
          <button className="btn-close-error" onClick={() => setErrorMessage(null)}>
            <X size={16} />
          </button>
        </div>
      )}

      {/* Fenêtre de discussion principale */}
      <main className="chat-container">
        <div className="messages-list" id="messages-list">
          {messages.length === 0 ? (
            <WelcomeHero onSelectSuggestion={handleSendMessage} />
          ) : (
            messages.map((msg) => (
              <MessageItem key={msg.id} message={msg} />
            ))
          )}

          {/* Indicateur de génération en cours */}
          {isLoading && (
            <div className="message-row assistant" id="generating-indicator">
              <div className="avatar bot">
                <span>🥗</span>
              </div>
              <div className="typing-indicator">
                <span className="typing-dot" />
                <span className="typing-dot" />
                <span className="typing-dot" />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Zone de saisie */}
        <MessageInput onSendMessage={handleSendMessage} isLoading={isLoading} />
      </main>

      {/* Modal du cadre d'utilisation */}
      <DisclaimerModal
        isOpen={isDisclaimerOpen}
        onClose={() => setIsDisclaimerOpen(false)}
      />
    </div>
  );
}
