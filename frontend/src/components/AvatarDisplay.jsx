import React from 'react';
import { useSpeech } from '../contexts/SpeechContext';

const AvatarDisplay = ({ 
  isProcessing, 
  isLoading, 
  isNodding, 
  isShaking, 
  avatarRef, 
  onClick, 
  dropletAvatar 
}) => {
  const { isTalking, isListening } = useSpeech();
  
  return (
    <div className="relative group perspective-2000 py-12">
      <div 
        ref={avatarRef}
        onClick={onClick}
        className={`
          w-72 h-72 md:w-96 md:h-96 rounded-full cursor-pointer relative
          transition-all duration-1000 ease-out preserve-3d
          ${isTalking ? 'scale-105 rotate-y-12' : 'hover:scale-102'}
          ${isNodding ? 'nod-animation' : ''}
          ${isShaking ? 'shake-animation' : ''}
        `}
      >
        {/* Advanced Multi-layered Glow */}
        <div className={`absolute inset-0 rounded-full bg-blue-500/10 blur-[100px] transition-all duration-1000 ${isTalking ? 'opacity-100 scale-125' : 'opacity-40'}`}></div>
        <div className={`absolute inset-0 rounded-full bg-cyan-400/5 blur-[60px] transition-all duration-1000 ${isListening ? 'opacity-100 scale-110' : 'opacity-0'}`}></div>
        
        {/* Core Avatar Container */}
        <div className={`
          absolute inset-0 rounded-full overflow-hidden shadow-[0_0_80px_rgba(0,0,0,0.5)]
          border-4 transition-colors duration-1000
          ${isTalking ? 'border-blue-400/50' : 'border-white/10'}
          ${isListening ? 'border-red-400/50' : ''}
        `}>
          <div className="absolute inset-0 bg-gradient-to-b from-blue-400/10 to-transparent z-10"></div>
          <img 
            src={dropletAvatar} 
            alt="Delta Intelligence" 
            className={`w-full h-full object-cover transition-all duration-1000 
              ${isTalking ? 'brightness-125 scale-110 saturate-125' : 'brightness-90 grayscale-[0.2]'}
              ${isListening ? 'sepia-[0.2] brightness-110' : ''}
            `} 
          />
        </div>

        {/* Tactical Status Ring */}
        <svg className="absolute -inset-8 w-[calc(100%+64px)] h-[calc(100%+64px)] pointer-events-none opacity-20">
           <circle cx="50%" cy="50%" r="48%" fill="none" stroke="white" strokeWidth="0.5" strokeDasharray="4 8" className="animate-[spin_60s_linear_infinite]" />
           <circle cx="50%" cy="50%" r="46%" fill="none" stroke="white" strokeWidth="1" strokeDasharray="100 200" className="animate-[spin_40s_linear_infinite_reverse]" />
        </svg>

        {/* HUD Elements */}
        <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-3">
          <div className="flex gap-2">
            {isListening && <div className="px-4 py-1.5 bg-red-500 text-[10px] font-black tracking-[0.2em] rounded-md shadow-[0_0_20px_rgba(239,68,68,0.4)] animate-pulse">LISTENING</div>}
            {isProcessing && <div className="px-4 py-1.5 bg-blue-500 text-[10px] font-black tracking-[0.2em] rounded-md shadow-[0_0_20px_rgba(59,130,246,0.4)] animate-bounce">PROCESSING</div>}
            {isLoading && <div className="px-4 py-1.5 bg-yellow-500 text-[10px] font-black tracking-[0.2em] rounded-md animate-pulse text-black">SYNCING</div>}
          </div>
          
          <div className="px-4 py-1 bg-white/5 backdrop-blur-md border border-white/10 rounded-full">
             <span className="text-[8px] uppercase tracking-[0.4em] font-bold text-white/40">Neural Interface v2.0</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AvatarDisplay;