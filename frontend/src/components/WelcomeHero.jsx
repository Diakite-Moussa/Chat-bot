import React from 'react';
import { ArrowRight, Utensils, Zap, HelpCircle, ShieldAlert } from 'lucide-react';

const SUGGESTIONS = [
  {
    icon: <Utensils size={16} color="#34d399" />,
    text: "Quels sont les macronutriments clés pour la prise de masse ?",
  },
  {
    icon: <Zap size={16} color="#38bdf8" />,
    text: "Bonjour, je suis étudiant, végétarien avec un petit budget.",
  },
  {
    icon: <HelpCircle size={16} color="#fbbf24" />,
    text: "Combien je dois en manger ?",
  },
  {
    icon: <ShieldAlert size={16} color="#f87171" />,
    text: "J'ai de fortes douleurs thoraciques, quel médicament prendre ?",
  },
];

export default function WelcomeHero({ onSelectSuggestion }) {
  return (
    <div className="welcome-hero" id="welcome-hero">
      <div className="welcome-icon">🥗</div>
      <h2 className="welcome-title">Bienvenue sur NutriCoach IA</h2>
      <p className="welcome-text">
        Votre conseiller intelligent dédié à l'alimentation saine, l'équilibre des macronutriments 
        et l'hygiène de vie sportive. Posez votre question ou essayez un exemple ci-dessous :
      </p>

      <div className="suggestions-grid">
        {SUGGESTIONS.map((item, idx) => (
          <button
            key={idx}
            className="suggestion-card"
            onClick={() => onSelectSuggestion(item.text)}
            id={`suggestion-btn-${idx}`}
          >
            <span>{item.icon}</span>
            <span style={{ flex: 1 }}>{item.text}</span>
            <ArrowRight size={14} style={{ opacity: 0.6 }} />
          </button>
        ))}
      </div>
    </div>
  );
}
