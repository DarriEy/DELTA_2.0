import React from 'react';

const EducationalPanel = ({ content }) => {
  if (!content) return null;
  
  return (
    <div className="space-y-10 animate-in fade-in duration-700">
      <div className="space-y-2">
        <p className="text-[9px] font-bold text-white/20 uppercase tracking-[0.4em]">Academy Node</p>
        <h4 className="text-2xl font-light text-white/90 tracking-tight">{content.topic}</h4>
      </div>

      <p className="text-sm text-white/50 leading-relaxed font-light">
        {content.explanation}
      </p>

      <div className="pt-6 border-t border-white/[0.03]">
         <p className="text-[9px] font-bold text-white/20 uppercase tracking-[0.4em] mb-3">Insight</p>
         <p className="text-xs italic text-white/40 leading-relaxed font-light">{content.fact}</p>
      </div>
    </div>
  );
};

export default EducationalPanel;
