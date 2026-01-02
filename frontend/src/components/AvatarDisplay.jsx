import React from 'react';

const AvatarDisplay = ({ 
  isProcessing, 
  isLoading, 
  isNodding, 
  isShaking, 
  avatarRef, 
  onClick, 
  dropletAvatar 
}) => {
  return (
    <div className="relative group py-8">
      <div 
        ref={avatarRef}
        onClick={onClick}
        className={`
          w-64 h-64 md:w-72 md:h-72 rounded-full cursor-pointer relative
          transition-all duration-1000 ease-in-out
          ${isProcessing ? 'scale-105' : 'hover:scale-102'}
          ${isNodding ? 'nod-animation' : ''}
          ${isShaking ? 'shake-animation' : ''}
        `}
      >
        {/* Subtle Ambient Glow */}
        <div className={`absolute inset-0 rounded-full bg-blue-500/5 blur-3xl transition-all duration-1000 ${isProcessing ? 'opacity-100 scale-110' : 'opacity-0'}`}></div>
        
        {/* Simple Avatar Container */}
        <div className={`
          absolute inset-0 rounded-full overflow-hidden
          border transition-colors duration-1000
          ${isProcessing ? 'border-blue-500/40' : 'border-white/[0.05]'}
        `}>
          <img 
            src={dropletAvatar} 
            alt="Delta" 
            className={`w-full h-full object-cover transition-all duration-1000 opacity-60
              ${isProcessing ? 'opacity-100 brightness-110' : ''}
            `} 
          />
        </div>

        {/* Minimalist HUD */}
        <div className="absolute -bottom-12 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2">
          <div className="flex gap-2">
            {isProcessing && <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-bounce shadow-[0_0_8px_#3b82f6]"></div>}
            {isLoading && <div className="w-1.5 h-1.5 rounded-full bg-yellow-500 animate-pulse"></div>}
          </div>
          <span className="text-[8px] uppercase tracking-[0.4em] font-medium text-white/10">Delta Core</span>
        </div>
      </div>
    </div>
  );
};

export default AvatarDisplay;
