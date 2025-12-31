import React from 'react';
import { useConversation } from '../contexts/ConversationContext';

const ModeSelector = ({ onSwitchMode, onGetSummary }) => {
  const { activeMode } = useConversation();
  
  const modes = [
    { id: 'general', icon: '🧠', label: 'Dashboard' },
    { id: 'educational', icon: '🎓', label: 'Academy' },
    { id: 'modeling', icon: '⚙️', label: 'Simulator' },
    { id: 'dataAnalysis', icon: '📊', label: 'Analytics' }
  ];

  return (
    <nav className="absolute left-8 top-1/2 -translate-y-1/2 z-20 flex flex-col gap-6">
      <div className="flex flex-col gap-3 p-2 bg-white/5 backdrop-blur-2xl border border-white/10 rounded-3xl shadow-2xl">
        {modes.map(mode => (
          <button
            key={mode.id}
            onClick={() => onSwitchMode(mode.id)}
            className={`flex items-center gap-4 p-4 rounded-2xl transition-all duration-500 group relative
              ${activeMode === mode.id 
                ? 'bg-blue-600/40 text-white shadow-[0_0_20px_rgba(37,99,235,0.3)] border-blue-400/30' 
                : 'text-white/50 hover:text-white hover:bg-white/5 border-transparent'
              } border`}
          >
            <span className="text-2xl group-hover:scale-110 transition-transform duration-300">{mode.icon}</span>
            <div className={`flex flex-col items-start transition-all duration-500 overflow-hidden ${activeMode === mode.id ? 'w-24 opacity-100' : 'w-0 opacity-0'}`}>
              <span className="text-xs font-bold uppercase tracking-widest leading-none mb-1">{mode.label}</span>
              <span className="text-[10px] text-white/40 whitespace-nowrap">Active Mode</span>
            </div>
            {activeMode === mode.id && (
              <div className="absolute -left-1 top-1/2 -translate-y-1/2 w-1.5 h-8 bg-blue-400 rounded-full shadow-[0_0_10px_rgba(96,165,250,0.8)]"></div>
            )}
          </button>
        ))}
      </div>
      
      <button 
        onClick={onGetSummary}
        className="flex items-center gap-4 p-5 rounded-3xl bg-purple-600/20 border border-purple-500/20 backdrop-blur-xl hover:bg-purple-600/30 transition-all group shadow-xl"
        title="Generate Insights Summary"
      >
        <span className="text-2xl group-hover:rotate-12 transition-transform duration-300">📝</span>
        <div className="flex flex-col items-start">
           <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-purple-300">Insights</span>
           <span className="text-[9px] text-white/40">Summary</span>
        </div>
      </button>
    </nav>
  );
};

export default ModeSelector;