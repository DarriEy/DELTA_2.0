import React from 'react';

const ModelingPanel = ({ 
  selectedModel, 
  setSelectedModel, 
  onJobSubmit, 
  isProcessing, 
  jobStatus 
}) => {
  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-right-8 duration-700">
      <div className="grid gap-6">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-[10px] uppercase tracking-[0.3em] text-white/40 font-bold">Computational Engine</label>
            <span className="text-[9px] px-2 py-0.5 bg-blue-500/10 text-blue-400 border border-blue-400/20 rounded-md font-bold">v2.4.0</span>
          </div>
          <select 
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="w-full bg-white/5 border border-white/10 rounded-2xl p-4 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all cursor-pointer hover:bg-white/10"
          >
            <option value="SUMMA" className="bg-slate-900">SUMMA • Physics-Based</option>
            <option value="VIC" className="bg-slate-900">VIC • Macroscale</option>
            <option value="PRMS" className="bg-slate-900">PRMS • Event-Based</option>
          </select>
          <p className="text-[10px] text-white/30 px-1 italic">Select a model architecture for the simulation run.</p>
        </div>

        <div className="p-6 bg-blue-500/5 border border-blue-500/10 rounded-3xl space-y-4">
           <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center text-blue-400 text-xl shadow-inner">
                📍
              </div>
              <div>
                <h5 className="text-xs font-bold text-white/80 uppercase tracking-widest">Target Watershed</h5>
                <p className="text-[10px] text-blue-400/60 font-mono italic">Bow_at_Banff_lumped.nc</p>
              </div>
           </div>
        </div>
      </div>
      
      <button 
        onClick={onJobSubmit}
        disabled={isProcessing}
        className={`w-full py-5 rounded-2xl font-black text-xs uppercase tracking-[0.4em] shadow-2xl transition-all active:scale-[0.98] flex items-center justify-center gap-4
          ${isProcessing 
            ? 'bg-slate-800 text-white/20 cursor-not-allowed' 
            : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-blue-900/40'
          }`}
      >
        {isProcessing ? (
          <>
            <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
            Executing...
          </>
        ) : (
          <>
            <span>⚡</span> Compute Simulation
          </>
        )}
      </button>

      {jobStatus && (
        <div className="p-6 bg-slate-900/40 border border-white/5 rounded-3xl space-y-4 animate-in zoom-in-95 duration-500">
          <div className="flex items-center justify-between">
             <div className="flex items-center gap-2">
               <div className="w-2 h-2 rounded-full bg-blue-500 animate-ping"></div>
               <span className="text-[10px] uppercase font-bold tracking-widest text-blue-100">Task Lifecycle</span>
             </div>
             <span className="text-[9px] px-3 py-1 bg-blue-500/20 text-blue-300 rounded-full font-mono border border-blue-500/30 uppercase">{jobStatus}</span>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-[9px] text-white/30 uppercase tracking-tighter">
               <span>Allocating Resources</span>
               <span>74%</span>
            </div>
            <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden p-[1px] border border-white/10">
               <div className="h-full bg-gradient-to-r from-blue-600 to-cyan-400 rounded-full shadow-[0_0_10px_rgba(6,182,212,0.5)] animate-pulse" style={{width: '74%'}}></div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelingPanel;