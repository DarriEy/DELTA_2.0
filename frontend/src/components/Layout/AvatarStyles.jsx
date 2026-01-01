import React from "react";

const AvatarStyles = () => {
  return (
    <style
      dangerouslySetInnerHTML={{
        __html: `
        @keyframes nod {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-20px); }
        }
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-15px); }
          75% { transform: translateX(15px); }
        }
        @keyframes pulse-red {
          0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
          50% { box-shadow: 0 0 0 20px rgba(239, 68, 68, 0); }
        }
        .nod-animation { animation: nod 0.6s ease-in-out infinite; }
        .shake-animation { animation: shake 0.6s ease-in-out infinite; }
        .listening-animation { animation: pulse-red 2s infinite; }
        .perspective-2000 { perspective: 2000px; }
        .preserve-3d { transform-style: preserve-3d; }
        .scrollbar-hide::-webkit-scrollbar { display: none; }
        .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
        .markdown-content p { margin-bottom: 1rem; color: rgba(255,255,255,0.8); }
        .markdown-content code { background: rgba(255,255,255,0.05); padding: 0.2rem 0.4rem; border-radius: 6px; font-family: monospace; color: #60a5fa; }
      `,
      }}
    />
  );
};

export default AvatarStyles;
