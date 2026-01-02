import React from "react";

const HudFooter = () => {
  return (
    <footer className="absolute bottom-12 left-16 right-16 z-20 flex justify-between items-end pointer-events-none opacity-40 hover:opacity-100 transition-opacity duration-500">
      <div className="flex flex-col gap-6 pointer-events-auto">
        <div className="flex gap-12">
          {[
            { label: "Environment", value: "Stateless" },
            { label: "Engine", value: "Gemini-Flash" },
          ].map((stat, i) => (
            <div
              key={i}
              className="flex flex-col gap-1"
            >
              <span className="text-[7px] uppercase font-bold text-slate-500 tracking-[0.3em]">
                {stat.label}
              </span>
              <span className="text-[10px] font-medium text-slate-300 tracking-wider">
                {stat.value}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="text-right pointer-events-auto">
        <p className="text-[8px] uppercase tracking-[0.4em] text-slate-600 font-medium">
          Scientific Computing <span className="text-slate-400">Node 01</span>
        </p>
      </div>
    </footer>
  );
};

export default HudFooter;
