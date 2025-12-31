import React from 'react';

const DataAnalysisPanel = ({ content }) => {
  if (!content) return null;

  return (
    <div className="space-y-12 animate-in fade-in duration-700">
      <div className="space-y-2">
        <p className="text-[9px] uppercase tracking-[0.4em] text-white/20 font-bold">Analytics Node</p>
        <h4 className="text-2xl font-light text-white/90 tracking-tight">{content.dataset}</h4>
      </div>

      <div className="grid grid-cols-2 gap-y-8 gap-x-4">
        {content.metrics.map((m, i) => (
          <div key={i} className="space-y-1">
             <p className="text-[8px] uppercase tracking-[0.4em] text-white/20 font-bold">{m.label}</p>
             <p className="text-xl font-light text-white/80">{m.value}</p>
          </div>
        ))}
      </div>

      <div className="pt-8 border-t border-white/[0.03]">
         <p className="text-[9px] font-bold uppercase tracking-[0.4em] text-white/20 mb-3">Summary</p>
         <p className="text-xs leading-relaxed text-white/40 italic font-light">
           "{content.summary}"
         </p>
      </div>
    </div>
  );
};

export default DataAnalysisPanel;
