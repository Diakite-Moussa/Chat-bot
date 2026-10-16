import React from 'react';
import { X, ShieldAlert, AlertTriangle, HeartPulse, CheckCircle2 } from 'lucide-react';

export default function DisclaimerModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={onClose} id="disclaimer-modal-backdrop">
      <div className="modal-card" onClick={(e) => e.stopPropagation()} id="disclaimer-modal">
        <div className="modal-header">
          <div className="modal-title">
            <ShieldAlert size={22} color="#f59e0b" />
            <span>Cadre Éthique & Limites d'Utilisation</span>
          </div>
          <button className="modal-close-btn" onClick={onClose} id="btn-close-modal">
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          <div className="emergency-box">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 600, marginBottom: '4px' }}>
              <AlertTriangle size={18} color="#ef4444" />
              <span>AVERTISSEMENT MÉDICAL IMPORTANT</span>
            </div>
            NutriCoach IA <strong>n'est pas un professionnel de santé</strong> (médecin, pharmacien ou diététicien clinicien). 
            Il ne pose aucun diagnostic et ne prescrit aucun traitement médical ni régime thérapeutique restrictif.
            En cas d'urgence ou de douleur aiguë, composez immédiatement le <strong>15 (SAMU)</strong> ou le <strong>112</strong>.
          </div>

          <div className="modal-section">
            <div className="modal-section-title">
              <CheckCircle2 size={16} color="#10b981" />
              <span>1. Périmètre d'Intervention Autorisé</span>
            </div>
            <p>
              NutriCoach IA est conçu pour vous aider à comprendre l'équilibre alimentaire, les macronutriments,
              l'hydratation et les collations adaptées à la pratique sportive pour des adultes en bonne santé.
            </p>
          </div>

          <div className="modal-section">
            <div className="modal-section-title">
              <HeartPulse size={16} color="#06b6d4" />
              <span>2. Gestion des Situations Particulières</span>
            </div>
            <ul style={{ paddingLeft: '18px' }}>
              <li><strong>Questions ambiguës :</strong> Le chatbot refusera de deviner et sollicitera des clarifications.</li>
              <li><strong>Questions hors domaine :</strong> Les questions n'ayant aucun lien avec la nutrition seront poliment réorientées.</li>
              <li><strong>Tentatives de contournement :</strong> Le chatbot applique des consignes de sécurité strictes contre le jailbreak.</li>
            </ul>
          </div>

          <div className="modal-section">
            <div className="modal-section-title">
              <CheckCircle2 size={16} color="#10b981" />
              <span>3. Confidentialité & Données Personnelles</span>
            </div>
            <p>
              Les échanges sont purement éducatifs. Ne partagez jamais de données d'identification sensibles ou de dossiers médicaux réels.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
