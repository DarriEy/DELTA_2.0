import React, { useState, useRef, useMemo } from "react";
import { useConversation } from "./contexts/ConversationContext";
import { useSpeech } from "./contexts/SpeechContext";
import { useBackgrounds } from "./hooks/useBackgrounds";
import SummaryModal from './components/Modals/SummaryModal';
import dropletAvatar from './assets/Droplet_avatar.png';
import { useInitialization } from "./hooks/useInitialization";
import { useSpeechInteraction } from "./hooks/useSpeechInteraction";
import { useModeContent } from "./hooks/useModeContent";
import { useSummary } from "./hooks/useSummary";
import { useModelingJob } from "./hooks/useModelingJob";
import { useBackgroundStyle } from "./hooks/useBackgroundStyle";

// Sub-components
import ChatPanel from "./components/ChatPanel";
import ModeSelector from "./components/ModeSelector";
import AvatarDisplay from "./components/AvatarDisplay";
import HudHeader from "./components/Layout/HudHeader";
import HudFooter from "./components/Layout/HudFooter";
import AvatarStyles from "./components/Layout/AvatarStyles";
import DynamicWorkspace from "./components/DynamicWorkspace";

const AnimatedAvatar = () => {
  const { 
    currentConversationId, 
    activeMode,
    setActiveMode,
    sendMessage,
    addLocalAssistantMessage,
    isLoading: isConversationLoading,
    createNewConversation
  } = useConversation();
  
  const { isListening, isTalking, startListening, speak } = useSpeech();
  const { backgrounds, generateBackground, isLoading: isBackgroundLoading } = useBackgrounds();

  const [selectedModel, setSelectedModel] = useState("SUMMA");

  const isLoading = isConversationLoading || isBackgroundLoading;
  const avatarRef = useRef(null);

  useInitialization({
    currentConversationId,
    createNewConversation,
    generateBackground,
  });

  const {
    isNodding,
    isShaking,
    isProcessing,
    isChatActive,
    setIsProcessing,
    handleAvatarClick,
    triggerShake,
  } = useSpeechInteraction({
    sendMessage,
    addLocalAssistantMessage,
    startListening,
    speak,
    isListening,
    isTalking,
  });

  const {
    showContentFrame,
    currentEducationalContent,
    currentModelingContent,
    currentDataAnalysisContent,
    switchMode,
  } = useModeContent({
    activeMode,
    setActiveMode,
    backgrounds,
    generateBackground,
  });

  const { summaryText, showSummaryModal, setShowSummaryModal, handleGetSummary } =
    useSummary({ currentConversationId, setIsProcessing });

  const { jobStatus, handleModelingJobSubmit } = useModelingJob({
    setIsProcessing,
    onShake: triggerShake,
  });

  const backgroundStyle = useBackgroundStyle(activeMode, backgrounds);

  const finalIsProcessing = isProcessing;

  return (
    <div 
      className="min-h-screen w-screen flex flex-col items-center justify-center font-sans text-white selection:bg-blue-500/30 transition-all duration-1000 bg-slate-950"
      style={backgroundStyle}
    >
      
      <HudHeader dropletAvatar={dropletAvatar} />

      <ModeSelector onSwitchMode={switchMode} onGetSummary={handleGetSummary} />

      <main className="z-10 w-full max-w-[1400px] px-12 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
        
        {/* Left: Avatar Display */}
        <div className="lg:col-span-5 flex justify-center">
          <AvatarDisplay 
            isProcessing={finalIsProcessing}
            isLoading={isLoading}
            isNodding={isNodding}
            isShaking={isShaking}
            avatarRef={avatarRef}
            onClick={handleAvatarClick}
            dropletAvatar={dropletAvatar}
          />
        </div>

        {/* Right: Functional HUD */}
        <div className="lg:col-span-7 space-y-8 h-[700px] flex flex-col justify-center">
          <div className="grid grid-cols-1 gap-8 h-full py-12">
            
            {/* Upper: Chat Stream */}
            <ChatPanel isActive={isChatActive} />

            {/* Lower: Dynamic Workspace */}
            <DynamicWorkspace 
              activeMode={activeMode}
              showContentFrame={showContentFrame}
              currentEducationalContent={currentEducationalContent}
              selectedModel={selectedModel}
              setSelectedModel={setSelectedModel}
              handleModelingJobSubmit={handleModelingJobSubmit}
              isProcessing={finalIsProcessing}
              jobStatus={jobStatus}
              currentDataAnalysisContent={currentDataAnalysisContent}
            />

          </div>
        </div>
      </main>

      <HudFooter />

      {showSummaryModal && <SummaryModal summary={summaryText} onClose={() => setShowSummaryModal(false)} />}

      <AvatarStyles />
    </div>
  );
};

export default AnimatedAvatar;
