import React from "react";

const HudHeader = ({ dropletAvatar }) => {
  return (
    <header className="absolute top-0 left-0 right-0 z-30 px-12 py-10 flex justify-between items-center pointer-events-none">
      <div className="flex items-center gap-6 pointer-events-auto group">
        <div className="relative">
          <div className="absolute inset-0 bg-blue-500 blur-2xl opacity-20 group-hover:opacity-40 transition-opacity"></div>
          <div className="w-16 h-16 rounded-2xl bg-white/5 backdrop-blur-3xl border border-white/10 flex items-center justify-center overflow-hidden shadow-2xl relative z-10">
            <img
              src={dropletAvatar}
              alt="Logo"
              className="w-10 h-10 object-contain"
            />
          </div>
        </div>
        <div>
          <h1 className="text-3xl font-black tracking-tighter text-white drop-shadow-2xl uppercase italic">
            DELTA <span className="text-blue-500 not-italic font-light">2.0</span>
          </h1>
          <div className="flex items-center gap-2">
            <div className="h-[1px] w-4 bg-blue-500/50"></div>
            <span className="text-[10px] font-bold text-white/30 uppercase tracking-[0.4em]">
              Integrated Intelligence Node
            </span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-8 pointer-events-auto">
        <div className="flex flex-col items-end">
          <span className="text-xs font-black text-blue-400">DEC 30 2025</span>
          <span className="text-[10px] text-white/30 font-mono tracking-widest uppercase">
            Nodes Online
          </span>
        </div>
      </div>
    </header>
  );
};

export default HudHeader;
