import React from "react";

const HudHeader = ({ dropletAvatar }) => {
  return (
    <header className="absolute top-0 left-0 right-0 z-30 px-16 py-12 flex justify-between items-start pointer-events-none">
      <div className="flex items-center gap-8 pointer-events-auto group">
        <div className="relative">
          <div className="w-12 h-12 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center overflow-hidden grayscale opacity-80 group-hover:grayscale-0 group-hover:opacity-100 transition-all duration-500">
            <img
              src={dropletAvatar}
              alt="Logo"
              className="w-6 h-6 object-contain"
            />
          </div>
        </div>
        <div className="space-y-1">
          <h1 className="text-2xl font-light tracking-[0.2em] text-slate-100 uppercase">
            Delta <span className="font-semibold text-slate-400">Project</span>
          </h1>
          <div className="flex items-center gap-3">
            <span className="text-[10px] font-medium text-slate-500 uppercase tracking-[0.3em]">
              Hydrological Research Unit
            </span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-12 pointer-events-auto border-l border-slate-800 pl-12 h-12">
        <div className="flex flex-col items-start justify-center">
          <span className="text-[10px] font-bold text-slate-400 tracking-[0.2em] uppercase">Status</span>
          <span className="text-[10px] text-emerald-500/80 font-medium tracking-widest uppercase flex items-center gap-2">
            <div className="w-1 h-1 rounded-full bg-emerald-500 animate-pulse"></div> Online
          </span>
        </div>
      </div>
    </header>
  );
};

export default HudHeader;
