import React from 'react';
import { Sparkles, RefreshCw, ShieldAlert, Cpu } from 'lucide-react';

export default function Header({ 
  backendStatus, 
  onResetConversation, 
  onOpenDisclaimer,
  isResetting 
}) {
  return (
    <header className="app-header" id="app-header">
      <div className="brand-section">
        <div className="brand-logo-wrap">
          <span>🥗</span>
        </div>
        <div>
          <h1 className="brand-title">
            NutriCoach IA <Sparkles size={16} color="#34d399" />
          </h1>
          <p className="brand-subtitle">
            Conseiller expert en nutrition, bien-être et sport
          </p>
        </div>
      </div>

      <div className="header-actions">
        {/* Statut Backend en direct */}
        <div className="status-badge" title={backendStatus?.online ? `En ligne (${backendStatus.provider || 'API'})` : "Backend hors ligne"}>
          <span className={`status-dot ${backendStatus?.online ? 'online' : 'offline'}`} />
          <span>{backendStatus?.online ? 'API En ligne' : 'Déconnecté'}</span>
        </div>

        {/* Bouton Limites & Sécurité */}
        <button 
          className="btn-header"
          onClick={onOpenDisclaimer}
          id="btn-open-disclaimer"
          title="Consulter les limites d'utilisation et le cadre éthique"
        >
          <ShieldAlert size={15} color="#38bdf8" />
          <span>Limites d'utilisation</span>
        </button>

        {/* Bouton Nouvelle conversation */}
        <button 
          className="btn-header primary"
          onClick={onResetConversation}
          disabled={isResetting}
          id="btn-new-conversation"
          title="Commencer une nouvelle conversation"
        >
          <RefreshCw size={15} className={isResetting ? "animate-spin" : ""} />
          <span>Nouvelle discussion</span>
        </button>
      </div>
    </header>
  );
}
