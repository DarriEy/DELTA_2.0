import React from 'react';
import { useConversation } from '../contexts/ConversationContext';
import { apiClient } from '../api/client';

const ModeSelector = ({ onSwitchMode, onGetSummary }) => {
  const { activeMode } = useConversation();

  const modes = [
    { id: 'general', icon: '🧠', label: 'General' },
    { id: 'educational', icon: '🎓', label: 'Learn' },
    { id: 'modeling', icon: '⚙️', label: 'Model' },
    { id: 'dataAnalysis', icon: '📊', label: 'Analyze' }
  ];

  return (
    <nav className="absolute right-8 top-1/2 -translate-y-1/2 z-20 flex flex-col gap-4">
      {modes.map(mode => (
        <button
          key={mode.id}
          onClick={() => onSwitchMode(mode.id)}
          className={`flex items-center gap-3 p-3 rounded-2xl backdrop-blur-xl transition-all duration-300 group
            ${activeMode === mode.id 
              ? 'bg-blue-500/40 border-blue-400/50 shadow-[0_0_20px_rgba(59,130,246,0.5)]' 
              : 'bg-white/10 border-white/10 hover:bg-white/20'
            } border`}
        >
          <span className="text-2xl group-hover:scale-110 transition-transform">{mode.icon}</span>
          <span className={`text-sm font-medium transition-all ${activeMode === mode.id ? 'opacity-100 w-20' : 'opacity-0 w-0 overflow-hidden'}`}>
            {mode.label}
          </span>
        </button>
      ))}
      
      <button 
        onClick={onGetSummary}
        className="mt-8 flex items-center gap-3 p-3 rounded-2xl bg-purple-500/30 border border-purple-400/50 backdrop-blur-xl hover:bg-purple-500/40 transition-all group"
        title="Session Summary"
      >
        <span className="text-2xl group-hover:rotate-12 transition-transform">📝</span>
      </button>
    </nav>
  );
};

export default ModeSelector;
