import React, { useState, useEffect, useRef } from "react";
import { useConversation } from "./contexts/ConversationContext";
import { useSpeech } from "./contexts/SpeechContext";
import { useBackgrounds } from "./hooks/useBackgrounds";
import educationalContent from "./educationalContent.json";
import modelingContent from "./modelingContent.json";
import dataAnalysisContent from "./dataAnalysisContent.json";
import SummaryModal from './summaryModal';
import dropletAvatar from './assets/Droplet_avatar.png';
import { apiClient } from "./api/client";

// Sub-components
import ChatPanel from "./components/ChatPanel";
import ModeSelector from "./components/ModeSelector";
import AvatarDisplay from "./components/AvatarDisplay";
import EducationalPanel from "./components/ControlPanels/EducationalPanel";
import ModelingPanel from "./components/ControlPanels/ModelingPanel";
import DataAnalysisPanel from "./components/ControlPanels/DataAnalysisPanel";

const AnimatedAvatar = () => {
  const { 
    currentConversationId, 
    conversationHistory, 
    activeMode,
    setActiveMode,
    sendMessage,
    isLoading: isConversationLoading,
    createNewConversation
  } = useConversation();
  
  const { isListening, startListening, speak } = useSpeech();
  const { backgrounds, generateBackground, isLoading: isBackgroundLoading } = useBackgrounds();

  const [isNodding, setIsNodding] = useState(false);
  const [isShaking, setIsShaking] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [introductionSpoken, setIntroductionSpoken] = useState(false);
  const [showContentFrame, setShowContentFrame] = useState(false);
  const [selectedModel, setSelectedModel] = useState("SUMMA");
  const [summaryText, setSummaryText] = useState("");
  const [showSummaryModal, setShowSummaryModal] = useState(false);
  const [jobStatus, setJobStatus] = useState(null);

  const [currentEducationalContent, setCurrentEducationalContent] = useState(null);
  const [currentModelingContent, setCurrentModelingContent] = useState(null);
  const [currentDataAnalysisContent, setCurrentDataAnalysisContent] = useState(null);

  const isLoading = isConversationLoading || isBackgroundLoading;
  const avatarRef = useRef(null);

  // --- Initial Setup ---
  useEffect(() => {
    const init = async () => {
      const imagePrompt = 'Please, render a highly detailed photorealistic, 4K image of a natural landscape showcasing a beautiful hydrological landscape feature. The setting should be a breathtaking natural environment. Emphasize realistic lighting, textures, and reflections in the water. Style should render with sharp focus and intricate details. Use a 16:9 aspect ratio.';
      generateBackground('general', imagePrompt);
      
      if (!currentConversationId) {
        await createNewConversation('general');
      }
    };
    init();
  }, []);

  const handleSpeechRecognitionResult = async (text) => {
    if (!text) return;
    setIsProcessing(true);
    try {
      const llmResponse = await sendMessage(text);
      if (llmResponse) {
         await speak(llmResponse);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleAvatarClick = () => {
    if (!introductionSpoken) {
      speak("Hi I'm Delta, your personal hydrological research assistant. How should we save the world today?")
        .then(() => setIntroductionSpoken(true));
    } else if (!isListening) {
      startListening(handleSpeechRecognitionResult, (error) => {
        console.error(`Speech recognition error: ${error}`);
      });
    }
  };

  const switchMode = async (mode) => {
    if (activeMode === mode) return;
    
    setShowContentFrame(false); 
    setActiveMode(mode);

    if (mode === 'educational') {
      setCurrentEducationalContent(educationalContent.hydrology101);
      if (!backgrounds.educational) {
        const prompt = 'Please generate a photorealistic image of a university classroom from the perspective of a student...';
        await generateBackground('educational', prompt);
      }
    } else if (mode === 'modeling') {
      setCurrentModelingContent(modelingContent.intro);
      if (!backgrounds.modeling) {
        const prompt = 'Please create a photorealistic image of the interior of an advanced hydrological monitoring space...';
        await generateBackground('modeling', prompt);
      }
    } else if (mode === 'dataAnalysis') {
      setCurrentDataAnalysisContent(dataAnalysisContent.intro);
      if (!backgrounds.dataAnalysis) {
        const prompt = 'Please generate a photorealistic, top-down view of a modern, hydrological data analysis idea board...';
        await generateBackground('dataAnalysis', prompt);
      }
    }
    setShowContentFrame(true);
  };

  const handleModelingJobSubmit = async () => {
    try {
      setIsProcessing(true);
      const data = await apiClient.post('/run_modeling', {
        model: selectedModel,
        job_type: "SIMULATION"
      });
      setJobStatus("PENDING");
    } catch (error) {
      console.error("Modeling Error:", error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleGetSummary = async () => {
    if (!currentConversationId) return;
    try {
      setIsProcessing(true);
      const data = await apiClient.get(`/summary/${currentConversationId}`);
      setSummaryText(data.summary);
      setShowSummaryModal(true);
    } catch (error) {
      console.error("Summary Error:", error);
    } finally {
      setIsProcessing(false);
    }
  };

  const getBackground = () => {
    switch (activeMode) {
      case 'educational': return backgrounds.educational || backgrounds.general;
      case 'modeling': return backgrounds.modeling || backgrounds.general;
      case 'dataAnalysis': return backgrounds.dataAnalysis || backgrounds.general;
      default: return backgrounds.general;
    }
  };

  return (
    <div 
      className="min-h-screen w-screen flex flex-col items-center justify-center font-sans text-white selection:bg-blue-500/30 transition-all duration-1000"
      style={{
        background: getBackground()?.startsWith('data:') || getBackground()?.startsWith('http') 
          ? `radial-gradient(circle at center, rgba(0,0,0,0.6) 0%, rgba(0,0,0,0.9) 100%), url(${getBackground()}) center/cover no-repeat` 
          : getBackground() || '#050505',
      }}
    >
      
      {/* HUD Header */}
      <header className="absolute top-0 left-0 right-0 z-30 px-12 py-10 flex justify-between items-center pointer-events-none">
        <div className="flex items-center gap-6 pointer-events-auto group">
          <div className="relative">
             <div className="w-12 h-12 rounded-xl bg-white/5 backdrop-blur-3xl border border-white/10 flex items-center justify-center overflow-hidden relative z-10">
                <img src={dropletAvatar} alt="Logo" className="w-8 h-8 opacity-80" />
             </div>
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tighter text-white uppercase italic">
              DELTA <span className="text-blue-500 not-italic font-light">2.5</span>
            </h1>
            <span className="text-[8px] font-bold text-white/20 uppercase tracking-[0.4em]">Integrated Intelligence</span>
          </div>
        </div>
      </header>

      <ModeSelector onSwitchMode={switchMode} onGetSummary={handleGetSummary} />

      <main className="z-10 w-full max-w-[1200px] px-12 grid grid-cols-1 lg:grid-cols-12 gap-16 items-center">
        
        {/* Central Avatar */}
        <div className="lg:col-span-4 flex justify-center">
          <AvatarDisplay 
            isProcessing={isProcessing}
            isLoading={isLoading}
            isNodding={isNodding}
            isShaking={isShaking}
            avatarRef={avatarRef}
            onClick={handleAvatarClick}
            dropletAvatar={dropletAvatar}
          />
        </div>

        {/* Workspace */}
        <div className="lg:col-span-8 flex flex-col gap-8 h-[600px] justify-center">
          <ChatPanel />
          <div className={`transition-all duration-700 flex-1 bg-white/[0.02] border border-white/[0.05] rounded-3xl p-10 overflow-y-auto scrollbar-hide ${showContentFrame ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4 pointer-events-none'}`}>
            {activeMode === 'educational' && <EducationalPanel content={currentEducationalContent} />}
            {activeMode === 'modeling' && (
              <ModelingPanel 
                selectedModel={selectedModel}
                setSelectedModel={setSelectedModel}
                onJobSubmit={handleModelingJobSubmit}
                isProcessing={isProcessing}
                jobStatus={jobStatus}
              />
            )}
            {activeMode === 'dataAnalysis' && <DataAnalysisPanel content={currentDataAnalysisContent} />}
            {activeMode === 'general' && (
              <div className="h-full flex flex-col items-center justify-center text-center space-y-6 animate-in fade-in duration-1000">
                <div className="w-16 h-16 bg-white/[0.03] border border-white/[0.05] rounded-2xl flex items-center justify-center text-3xl">🌍</div>
                <div className="space-y-2">
                  <h4 className="text-xl font-light uppercase tracking-[0.3em]">Command Center</h4>
                  <p className="text-xs text-white/30 tracking-widest leading-relaxed">
                    Select a research node to begin.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Subtle Footer */}
      <footer className="absolute bottom-12 left-12 right-12 z-20 flex justify-between items-center text-[9px] uppercase tracking-[0.3em] text-white/10 font-medium">
        <div>© 2025 HYDROLOGICAL UNIT</div>
        <div className="flex gap-8">
          <span>LATENCY: 12MS</span>
          <span>SSL: SECURE</span>
        </div>
      </footer>

      {showSummaryModal && <SummaryModal summary={summaryText} onClose={() => setShowSummaryModal(false)} />}

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes nod { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-15px); } }
        @keyframes shake { 0%, 100% { transform: translateX(0); } 25% { transform: translateX(-10px); } 75% { transform: translateX(10px); } }
        .nod-animation { animation: nod 0.6s ease-in-out 2; }
        .shake-animation { animation: shake 0.6s ease-in-out 2; }
        .perspective-2000 { perspective: 2000px; }
        .preserve-3d { transform-style: preserve-3d; }
        .scrollbar-hide::-webkit-scrollbar { display: none; }
        .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
        .markdown-content p { margin-bottom: 1rem; color: rgba(255,255,255,0.8); }
        .markdown-content code { background: rgba(255,255,255,0.05); padding: 0.2rem 0.4rem; border-radius: 6px; color: #60a5fa; }
      `}} />
    </div>
  );
};

export default AnimatedAvatar;
