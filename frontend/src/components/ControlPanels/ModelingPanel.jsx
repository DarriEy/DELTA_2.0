import React from 'react';

const ModelingPanel = ({ 
  selectedModel, 
  setSelectedModel, 
  onJobSubmit, 
  isProcessing, 
  jobStatus 
}) => {
  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-500">
      <div>
        <label className="text-[10px] uppercase tracking-widest text-white/50 mb-2 block">Model Selection</label>
        <select 
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
          className="w-full bg-white/10 border border-white/20 rounded-lg p-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          <option value="SUMMA" className="bg-slate-800">SUMMA (Structure for Unifying Multiple Modeling Alternatives)</option>
          <option value="VIC" className="bg-slate-800">VIC (Variable Infiltration Capacity)</option>
          <option value="PRMS" className="bg-slate-800">PRMS (Precipitation-Runoff Modeling System)</option>
        </select>
      </div>
      
      <button 
        onClick={onJobSubmit}
        disabled={isProcessing}
        className="w-full py-4 bg-blue-500 hover:bg-blue-400 disabled:opacity-50 rounded-xl font-bold shadow-lg transition-all active:scale-95 flex items-center justify-center gap-2"
      >
        <span>🚀</span> Run Simulation
      </button>

      {jobStatus && (
        <div className="p-4 bg-blue-600/20 border border-blue-400/30 rounded-xl">
          <div className="flex items-center justify-between mb-2">
             <span className="text-xs uppercase font-bold tracking-widest text-blue-200">Job Status</span>
             <span className="text-xs px-2 py-0.5 bg-blue-400/30 rounded-full font-mono">{jobStatus}</span>
          </div>
          <div className="w-full h-1 bg-white/10 rounded-full overflow-hidden">
             <div className="h-full bg-blue-400 animate-progress"></div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelingPanel;
