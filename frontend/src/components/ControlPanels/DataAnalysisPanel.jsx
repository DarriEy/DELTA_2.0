import React from 'react';

const DataAnalysisPanel = ({ content }) => {
  if (!content) return (
    <div className="h-full flex items-center justify-center opacity-30 italic text-sm text-center px-12">
      Initialize telemetry stream to analyze hydrological datasets...
    </div>
  );

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-right-8 duration-700">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h4 className="text-2xl font-black text-white tracking-tight">{content.dataset}</h4>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-purple-500 animate-pulse"></span>
            <span className="text-[10px] text-purple-400 font-bold uppercase tracking-widest">Analytics Online</span>
          </div>
        </div>
        <div className="text-right">
           <p className="text-[10px] text-white/30 uppercase tracking-widest font-bold">Confidence Score</p>
           <p className="text-xl font-mono font-black text-purple-400">98.2%</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {content.metrics.map((m, i) => (
          <div key={i} className="p-5 bg-slate-900/50 rounded-3xl border border-white/5 shadow-xl group hover:border-purple-500/30 transition-all duration-500">
             <p className="text-[9px] uppercase tracking-widest text-white/30 mb-2 font-bold group-hover:text-purple-400 transition-colors">{m.label}</p>
             <div className="flex items-baseline gap-2">
                <p className="text-2xl font-mono font-black text-white">{m.value}</p>
                <div className="w-1.5 h-1.5 rounded-full bg-purple-500/40"></div>
             </div>
          </div>
        ))}
      </div>

      <div className="relative p-6 bg-purple-600/5 border border-purple-500/20 rounded-[2rem] overflow-hidden group">
         <div className="absolute top-0 left-0 w-1 h-full bg-purple-500/40"></div>
         <h5 className="text-[9px] font-bold uppercase tracking-[0.2em] text-purple-400 mb-3 flex items-center gap-2">
           <span className="w-4 h-[1px] bg-purple-500/30"></span> Automated Summary
         </h5>
         <p className="text-xs leading-relaxed text-white/70 italic relative z-10 font-medium">
           "{content.summary}"
         </p>
      </div>

      <div className="flex gap-3">
         <button className="flex-1 py-4 bg-purple-600/20 border border-purple-500/30 rounded-2xl text-[9px] font-bold uppercase tracking-widest hover:bg-purple-600/30 transition-all">
           Export CSV
         </button>
         <button className="flex-1 py-4 bg-white/5 border border-white/10 rounded-2xl text-[9px] font-bold uppercase tracking-widest hover:bg-white/10 transition-all">
           View Raw Data
         </button>
      </div>
    </div>
  );
};

export default DataAnalysisPanel;