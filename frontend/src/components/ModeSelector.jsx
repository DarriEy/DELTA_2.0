import React from 'react';
import { useConversation } from '../contexts/ConversationContext';

const ModeSelector = ({ onSwitchMode, onGetSummary }) => {
  const { activeMode } = useConversation();
  
  const modes = [
    { id: 'general', icon: '🧠', label: 'Index' },
    { id: 'educational', icon: '🎓', label: 'Academy' },
    { id: 'modeling', icon: '⚙️', label: 'Compute' },
    { id: 'dataAnalysis', icon: '📊', label: 'Analytics' }
  ];

  return (
    <nav className="absolute left-12 top-1/2 -translate-y-1/2 z-20 flex flex-col gap-12">
      <div className="flex flex-col gap-8">
        {modes.map(mode => (
          <button
            key={mode.id}
            onClick={() => onSwitchMode(mode.id)}
            className={`flex items-center gap-4 transition-all duration-300 group
              ${activeMode === mode.id ? 'text-white' : 'text-white/20 hover:text-white/40'}`}
          >
            <span className="text-xl">{mode.icon}</span>
            <span className={`text-[10px] font-bold uppercase tracking-[0.4em] transition-all duration-500 overflow-hidden ${activeMode === mode.id ? 'w-24 opacity-100' : 'w-0 opacity-0'}`}>
              {mode.label}
            </span>
          </button>
        ))}
      </div>
      
      <button 
        onClick={onGetSummary}
        className="flex items-center gap-4 text-white/20 hover:text-white transition-all group"
        title="Summary"
      >
        <span className="text-xl">📝</span>
        <span className="text-[10px] font-bold uppercase tracking-[0.4em] w-0 opacity-0 group-hover:w-24 group-hover:opacity-100 transition-all duration-500">
          Summary
        </span>
      </button>
    </nav>
  );
};

export default ModeSelector;
