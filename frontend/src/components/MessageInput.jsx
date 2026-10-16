import React, { useState, useRef, useEffect } from 'react';
import { Send, CornerDownLeft, AlertCircle } from 'lucide-react';

export default function MessageInput({ onSendMessage, isLoading }) {
  const [text, setText] = useState('');
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e?.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || isLoading) return;

    onSendMessage(trimmed);
    setText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInput = (e) => {
    setText(e.target.value);
    // Auto-expand textarea
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 140) + 'px';
  };

  return (
    <div className="input-section">
      <form onSubmit={handleSubmit}>
        <div className="input-bar">
          <textarea
            ref={textareaRef}
            rows={1}
            value={text}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            placeholder={isLoading ? "NutriCoach IA réfléchit à votre réponse..." : "Posez une question sur votre alimentation, vos repas ou votre sport..."}
            className="chat-textarea"
            disabled={isLoading}
            id="chat-textarea"
            maxLength={2000}
          />

          <button
            type="submit"
            disabled={!text.trim() || isLoading}
            className="send-button"
            id="send-button"
            title="Envoyer le message (Entrée)"
          >
            <Send size={16} />
          </button>
        </div>

        <div className="input-footer">
          <div className="input-disclaimer-text">
            <span>💡 Entrée pour envoyer, Maj+Entrée pour un saut de ligne</span>
          </div>
          <div style={{ color: text.length > 1800 ? '#f87171' : 'inherit' }}>
            {text.length}/2000
          </div>
        </div>
      </form>
    </div>
  );
}
