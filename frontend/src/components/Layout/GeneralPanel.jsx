import React from "react";

const GeneralPanel = () => {
  return (
    <div className="h-full flex flex-col items-center justify-center text-center space-y-12 animate-in fade-in duration-1000">
      <div className="relative">
        <div className="w-20 h-20 bg-slate-900 border border-slate-800 rounded-full flex items-center justify-center text-3xl relative z-10 opacity-60 grayscale">
          🌍
        </div>
      </div>
      <div className="space-y-6">
        <h4 className="text-3xl font-light text-slate-100 tracking-[0.3em] uppercase">
          Core <span className="font-semibold text-slate-400">Directory</span>
        </h4>
        <div className="w-12 h-[1px] bg-slate-800 mx-auto"></div>
        <p className="max-w-xs mx-auto text-[11px] text-slate-500 leading-relaxed tracking-[0.1em] font-medium uppercase">
          Select a research node from the primary navigation interface to begin analysis.
        </p>
      </div>
    </div>
  );
};

export default GeneralPanel;
