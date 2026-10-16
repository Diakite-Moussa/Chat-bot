import React, { useState } from 'react';
import { User, Bot, Copy, Check } from 'lucide-react';

function FormattedContent({ content }) {
  // Découpage par ligne pour rendu propre (gras, listes à puces, retours à la ligne)
  const lines = content.split('\n');

  return (
    <div className="formatted-content">
      {lines.map((line, idx) => {
        const trimmed = line.trim();
        if (!trimmed) {
          return <div key={idx} style={{ height: '8px' }} />;
        }

        // Puces : "- " ou "• " ou "* "
        if (trimmed.startsWith('- ') || trimmed.startsWith('• ') || trimmed.startsWith('* ')) {
          const itemText = trimmed.substring(2);
          return (
            <div key={idx} style={{ display: 'flex', gap: '8px', marginBottom: '4px' }}>
              <span style={{ color: '#34d399' }}>•</span>
              <span dangerouslySetInnerHTML={{ __html: formatInline(itemText) }} />
            </div>
          );
        }

        // Titre Markdown "### " ou "## "
        if (trimmed.startsWith('### ')) {
          return (
            <h4 key={idx} style={{ color: '#34d399', margin: '8px 0 4px', fontWeight: 600 }}>
              {trimmed.substring(4)}
            </h4>
          );
        }
        if (trimmed.startsWith('## ')) {
          return (
            <h3 key={idx} style={{ color: '#22d3ee', margin: '10px 0 6px', fontWeight: 700 }}>
              {trimmed.substring(3)}
            </h3>
          );
        }

        // Paragraphe standard
        return (
          <p key={idx} dangerouslySetInnerHTML={{ __html: formatInline(line) }} />
        );
      })}
    </div>
  );
}

// Convertit **texte** en <strong>texte</strong>
function formatInline(text) {
  let res = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  return res;
}

export default function MessageItem({ message }) {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formattedTime = message.timestamp
    ? new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : '';

  return (
    <div className={`message-row ${isUser ? 'user' : 'assistant'}`}>
      <div className={`avatar ${isUser ? 'user' : 'bot'}`}>
        {isUser ? <User size={18} /> : <span>🥗</span>}
      </div>

      <div className="message-bubble">
        <FormattedContent content={message.content} />
        
        <div className="message-meta">
          <span>{formattedTime}</span>
          {!isUser && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              {message.provider && (
                <span className="message-provider-tag">
                  {message.provider}
                </span>
              )}
              <button
                onClick={handleCopy}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'inherit',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                }}
                title="Copier le message"
              >
                {copied ? <Check size={13} color="#34d399" /> : <Copy size={13} />}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
