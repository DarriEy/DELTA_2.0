import React from 'react';

const EducationalPanel = ({ content }) => {
  if (!content) return (
    <div className="h-full flex items-center justify-center opacity-30 italic text-sm">
      Select a module to begin learning...
    </div>
  );
  
  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-right-8 duration-700">
      <div className="space-y-2">
        <div className="flex items-center gap-2 text-[10px] font-bold text-blue-400 uppercase tracking-[0.3em]">
          <span>Module 01</span>
          <div className="h-[1px] w-8 bg-blue-500/30"></div>
          <span>Fundamental Concepts</span>
        </div>
        <h4 className="text-3xl font-black text-white leading-tight tracking-tight">{content.topic}</h4>
      </div>

      <div className="relative p-8 bg-white/5 border border-white/10 rounded-[2.5rem] shadow-2xl overflow-hidden group">
        <div className="absolute top-0 right-0 p-6 opacity-5 group-hover:opacity-10 transition-opacity">
           <span className="text-8xl font-black">🎓</span>
        </div>
        <p className="text-base text-white/70 leading-relaxed relative z-10 font-light">
          {content.explanation}
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4">
        <div className="p-6 bg-gradient-to-br from-blue-600/10 to-transparent border border-blue-500/20 rounded-3xl flex gap-5 items-center">
           <div className="w-14 h-14 rounded-2xl bg-blue-500/20 flex items-center justify-center text-2xl shadow-inner border border-blue-500/20">
              💡
           </div>
           <div className="space-y-1">
              <h5 className="text-[10px] font-bold text-blue-400 uppercase tracking-widest">Scientific Insight</h5>
              <p className="text-xs italic text-white/60 leading-snug">{content.fact}</p>
           </div>
        </div>
        
        <button className="w-full py-4 border border-white/10 rounded-2xl text-[10px] font-bold uppercase tracking-[0.3em] hover:bg-white/5 transition-all text-white/40 hover:text-white">
          Explore Advanced Literature →
        </button>
      </div>
    </div>
  );
};

export default EducationalPanel;