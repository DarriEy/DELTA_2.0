import React from 'react';

const DataAnalysisPanel = ({ content }) => {
  if (!content) return null;

  return (
    <div className="space-y-4 animate-in fade-in slide-in-from-right-4 duration-500">
      <h4 className="text-xl font-bold text-purple-300">Insights: {content.dataset}</h4>
      <div className="grid grid-cols-2 gap-4">
        {content.metrics.map((m, i) => (
          <div key={i} className="p-3 bg-white/5 rounded-lg border border-white/10">
             <p className="text-[10px] uppercase text-white/40">{m.label}</p>
             <p className="text-lg font-mono font-bold text-purple-200">{m.value}</p>
          </div>
        ))}
      </div>
      <div className="mt-4 p-4 bg-purple-500/10 border border-purple-500/30 rounded-xl">
         <p className="text-xs leading-relaxed text-white/70 italic">"{content.summary}"</p>
      </div>
    </div>
  );
};

export default DataAnalysisPanel;
