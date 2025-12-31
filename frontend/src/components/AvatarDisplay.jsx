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
    <div className="relative group perspective-1000">
      <div 
        ref={avatarRef}
        onClick={onClick}
        className={`
          w-64 h-64 md:w-80 md:h-80 rounded-full cursor-pointer relative
          transition-all duration-700 ease-out preserve-3d
          ${isTalking ? 'scale-105 shadow-[0_0_50px_rgba(59,130,246,0.6)]' : 'hover:scale-102'}
          ${isNodding ? 'nod-animation' : ''}
          ${isShaking ? 'shake-animation' : ''}
        `}
      >
        {/* Ambient Glows */}
        <div className={`absolute inset-0 rounded-full bg-blue-500/20 blur-3xl animate-pulse ${isTalking ? 'opacity-100' : 'opacity-0'}`}></div>
        
        {/* The Avatar Image */}
        <div className="absolute inset-0 rounded-full bg-gradient-to-b from-blue-400/20 to-purple-600/20 backdrop-blur-sm border-2 border-white/20 overflow-hidden shadow-2xl">
          <img 
            src={dropletAvatar} 
            alt="Delta Avatar" 
            className={`w-full h-full object-cover transition-all duration-500 ${isTalking ? 'brightness-110 saturate-110' : 'brightness-90 opacity-80'}`} 
          />
        </div>

        {/* Status Indicators */}
        <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-2">
          {isListening && <div className="px-4 py-1.5 bg-red-500/80 backdrop-blur-md rounded-full text-xs font-bold animate-pulse shadow-lg">LISTENING</div>}
          {isProcessing && <div className="px-4 py-1.5 bg-blue-500/80 backdrop-blur-md rounded-full text-xs font-bold animate-pulse shadow-lg">PROCESSING</div>}
          {isLoading && <div className="px-4 py-1.5 bg-yellow-500/80 backdrop-blur-md rounded-full text-xs font-bold animate-bounce shadow-lg">LOADING</div>}
        </div>
      </div>
    </div>
  );
};

export default AvatarDisplay;
