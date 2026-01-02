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
    <div className="relative py-12 flex flex-col items-center gap-8">
      <div 
        ref={avatarRef}
        onClick={onClick}
        className={`
          w-48 h-48 md:w-56 md:h-56 rounded-full cursor-pointer relative
          transition-all duration-1000 ease-in-out border
          ${isProcessing ? 'border-slate-400 scale-105' : 'border-slate-800 hover:border-slate-600'}
          ${isNodding ? 'nod-animation' : ''}
          ${isShaking ? 'shake-animation' : ''}
        `}
      >
        {/* Simple Avatar Container */}
        <div className="absolute inset-0 rounded-full overflow-hidden bg-slate-900">
          <img 
            src={dropletAvatar} 
            alt="Research Unit" 
            className={`w-full h-full object-cover transition-all duration-1000 grayscale
              ${isProcessing ? 'opacity-100' : 'opacity-40'}
            `} 
          />
        </div>
      </div>

      <div className="flex flex-col items-center gap-2">
        <span className="text-[10px] font-medium text-slate-500 uppercase tracking-[0.4em]">Core Interface</span>
        <div className="flex gap-3 h-1 items-center">
          {isProcessing && <div className="w-1 h-1 rounded-full bg-slate-400 animate-pulse"></div>}
          {isLoading && <div className="w-1 h-1 rounded-full bg-slate-600 animate-pulse"></div>}
        </div>
      </div>
    </div>
  );
};

export default AvatarDisplay;
