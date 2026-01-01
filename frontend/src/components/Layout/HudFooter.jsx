import React from "react";

const HudFooter = () => {
  return (
    <footer className="absolute bottom-10 left-12 right-12 z-20 flex justify-between items-end pointer-events-none">
      <div className="flex flex-col gap-4 pointer-events-auto">
        <div className="flex gap-6">
          {[
            { label: "Compute", value: "42.8 TFLOPS" },
            { label: "Latency", value: "14ms" },
            { label: "Model", value: "Gemini-2.0" },
          ].map((stat, i) => (
            <div
              key={i}
              className="px-5 py-3 bg-white/5 border border-white/10 backdrop-blur-md rounded-2xl flex flex-col"
            >
              <span className="text-[8px] uppercase font-bold text-white/20 mb-1">
                {stat.label}
              </span>
              <span className="text-xs font-mono font-black text-white/80">
                {stat.value}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="text-right pointer-events-auto">
        <p className="text-[9px] uppercase tracking-[0.4em] text-white/20 font-light leading-relaxed">
          Proprietary Intelligence Core
          <br />
          <span className="text-white/60 font-black">
            HYDROLOGICAL RESEARCH UNIT
          </span>
        </p>
      </div>
    </footer>
  );
};

export default HudFooter;
