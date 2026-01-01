import React from "react";

const GeneralPanel = () => {
  return (
    <div className="h-full flex flex-col items-center justify-center text-center space-y-8 animate-in fade-in zoom-in duration-1000">
      <div className="relative">
        <div className="absolute inset-0 bg-blue-500 blur-3xl opacity-10 animate-pulse"></div>
        <div className="w-24 h-24 bg-white/5 border border-white/10 rounded-[2rem] flex items-center justify-center text-5xl relative z-10 shadow-2xl">
          🌍
        </div>
      </div>
      <div className="space-y-4">
        <h4 className="text-4xl font-black text-white tracking-tighter uppercase italic">
          Welcome Commander
        </h4>
        <p className="max-w-md mx-auto text-sm text-white/40 leading-relaxed tracking-wide font-light">
          Delta is standing by. Access specialized hydrological nodes via the
          primary navigation interface on the left.
        </p>
      </div>
    </div>
  );
};

export default GeneralPanel;
