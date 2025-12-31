import React from 'react';

const ModelingPanel = ({ selectedModel, setSelectedModel, onJobSubmit, isProcessing, jobStatus }) => {
  return (
    <div className="space-y-12 animate-in fade-in duration-700">
      <div className="space-y-6">
        <div className="space-y-2">
          <label className="text-[9px] uppercase tracking-[0.4em] text-white/20 font-bold">Model Engine</label>
          <select 
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="w-full bg-transparent border-b border-white/10 py-4 text-sm font-light focus:outline-none focus:border-white/30 transition-all cursor-pointer"
          >
            <option value="SUMMA" className="bg-black">SUMMA Physics</option>
            <option value="VIC" className="bg-black">VIC Macroscale</option>
            <option value="PRMS" className="bg-black">PRMS Hydrology</option>
          </select>
        </div>

        <div className="py-4 border-b border-white/10">
           <p className="text-[9px] uppercase tracking-[0.4em] text-white/20 font-bold mb-1">Target</p>
           <p className="text-xs font-light text-white/60">Bow_at_Banff_lumped.nc</p>
        </div>
      </div>
      
      <button 
        onClick={onJobSubmit}
        disabled={isProcessing}
        className="w-full py-4 border border-white/10 hover:border-white/30 text-[10px] uppercase tracking-[0.5em] font-bold transition-all disabled:opacity-20"
      >
        {isProcessing ? 'Executing...' : 'Run Simulation'}
      </button>

      {jobStatus && (
        <div className="flex items-center justify-between pt-4">
          <span className="text-[9px] uppercase tracking-[0.4em] text-white/20 font-bold">Status</span>
          <span className="text-[9px] text-blue-400 font-bold uppercase tracking-[0.2em] animate-pulse">{jobStatus}</span>
        </div>
      )}
    </div>
  );
};

export default ModelingPanel;
