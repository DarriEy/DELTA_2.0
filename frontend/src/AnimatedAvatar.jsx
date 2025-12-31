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

const GlassCard = ({ children, className = "" }) => (
  <div className={`glass-card p-6 ${className}`}>
    {children}
  </div>
);

const AnimatedAvatar = () => {
  // Contexts
  const { 
    currentConversationId, 
    conversationHistory, 
    setConversationHistory,
    activeMode,
    setActiveMode,
    sendMessage,
    isLoading: isConversationLoading 
  } = useConversation();
  
  const { 
    isListening, 
    startListening, 
    speak, 
  } = useSpeech();
  
  const { 
    backgrounds, 
    generateBackground, 
    isLoading: isBackgroundLoading 
  } = useBackgrounds();

  // Local UI State
  const [isNodding, setIsNodding] = useState(false);
  const [isShaking, setIsShaking] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [introductionSpoken, setIntroductionSpoken] = useState(false);
  const [showContentFrame, setShowContentFrame] = useState(false);
  const [selectedModel, setSelectedModel] = useState("SUMMA");
  const [summaryText, setSummaryText] = useState("");
  const [showSummaryModal, setShowSummaryModal] = useState(false);
  const [jobStatus, setJobStatus] = useState(null);

  // Content Data
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

    // sendMessage now handles adding the user message and assistant placeholder to history
    try {
      const llmResponse = await sendMessage(text);
      if (llmResponse) {
         await speak(llmResponse);
      }
    } catch (error) {
      console.error(error);
      alert("Error processing request.");
    } finally {
      setIsProcessing(false);
    }
  };


  const handleStartListening = () => {
    startListening(handleSpeechRecognitionResult, (error) => {
      console.error(`Speech recognition error: ${error}`);
    });
  };

  const handleAvatarClick = async () => {
    if (!introductionSpoken) {
      const textToSpeak = "Hi I'm Delta, your personal hydrological research assistant. How should we save the world today?";
      try {
        await speak(textToSpeak);
        setIntroductionSpoken(true);
      } catch (error) {
        console.error(error);
      }
    } else if (!isListening) {
      handleStartListening();
    }
  };

  // --- Mode Handling ---
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
      setShowContentFrame(true);
    } else if (mode === 'modeling') {
      setCurrentModelingContent(modelingContent.intro);
      if (!backgrounds.modeling) {
        const prompt = 'Please create a photorealistic image of the interior of an advanced hydrological monitoring space...';
        await generateBackground('modeling', prompt);
      }
      setShowContentFrame(true);
    } else if (mode === 'dataAnalysis') {
      setCurrentDataAnalysisContent(dataAnalysisContent.intro);
      if (!backgrounds.dataAnalysis) {
        const prompt = 'Please generate a photorealistic, top-down view of a modern, hydrological data analysis idea board...';
        await generateBackground('dataAnalysis', prompt);
      }
      setShowContentFrame(true);
    } else {
      setShowContentFrame(false);
    }
  };

  const handleModelingJobSubmit = async () => {
    try {
      setIsProcessing(true);
      const data = await apiClient.post('/run_modeling', {
        model: selectedModel,
        job_type: "SIMULATION"
      });
      setJobStatus("PENDING");
      alert(`Job submitted! ID: ${data.job_id}`);
    } catch (error) {
      console.error("Modeling Error:", error);
      alert("Failed to submit modeling job.");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleGetSummary = async () => {
    if (!currentConversationId) {
        alert("No active conversation to summarize.");
        return;
    }
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
      className="min-h-screen w-screen relative overflow-hidden flex flex-col items-center justify-center font-sans text-white transition-all duration-1000"
      style={{
        background: getBackground()?.startsWith('data:') || getBackground()?.startsWith('http') 
          ? `url(${getBackground()}) center/cover no-repeat` 
          : getBackground() || 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
      }}
    >
      <div className="absolute inset-0 bg-black/40 z-0"></div>

      <header className="absolute top-8 left-8 z-20 flex items-center gap-4">
        <div className="w-12 h-12 rounded-full bg-blue-500/20 backdrop-blur-md border border-white/20 flex items-center justify-center overflow-hidden shadow-xl">
           <img src={dropletAvatar} alt="Logo" className="w-8 h-8 object-contain" />
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-white/90 drop-shadow-md">
          DELTA <span className="text-blue-400 font-light text-lg">HydroAI</span>
        </h1>
      </header>

      <ModeSelector 
        onSwitchMode={switchMode} 
        onGetSummary={handleGetSummary} 
      />

      <main className="z-10 w-full max-w-6xl px-8 flex flex-col items-center gap-8">
        
        <AvatarDisplay 
          isProcessing={isProcessing}
          isLoading={isLoading}
          isNodding={isNodding}
          isShaking={isShaking}
          avatarRef={avatarRef}
          onClick={handleAvatarClick}
          dropletAvatar={dropletAvatar}
        />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 w-full max-w-5xl">
          <ChatPanel />

          <GlassCard className={`h-[400px] transition-all duration-500 border-2 ${showContentFrame ? 'border-blue-400/30' : 'border-transparent opacity-60 grayscale'}`}>
            <div className="h-full flex flex-col">
              <div className="mb-4 pb-4 border-b border-white/10 flex items-center gap-2">
                <span className="text-xl">
                  {activeMode === 'educational' && '🎓'}
                  {activeMode === 'modeling' && '⚙️'}
                  {activeMode === 'dataAnalysis' && '📊'}
                  {activeMode === 'general' && '🧠'}
                </span>
                <h3 className="text-lg font-semibold uppercase tracking-wider text-blue-100">
                  {activeMode.replace(/([A-Z])/g, ' $1').trim()} Content
                </h3>
              </div>

              <div className="flex-1 overflow-y-auto pr-2 scrollbar-thin">
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
                  <div className="h-full flex flex-col items-center justify-center text-center p-8 space-y-4">
                    <div className="w-20 h-20 bg-blue-500/20 rounded-full flex items-center justify-center text-3xl mb-2 animate-bounce">🌍</div>
                    <h4 className="text-xl font-light">Welcome to the Future of Water</h4>
                    <p className="text-xs text-white/40 leading-relaxed uppercase tracking-widest">
                      Switch modes to access specialized hydrological research tools.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </GlassCard>
        </div>
      </main>

      <footer className="absolute bottom-8 left-8 right-8 z-20 flex justify-between items-end">
        <div className="flex flex-col gap-2">
           <div className="text-[10px] uppercase tracking-[0.3em] text-white/30 font-bold mb-1">Compute Environment</div>
           <div className="flex gap-4">
              <div className="px-3 py-1 bg-white/5 border border-white/10 backdrop-blur-md rounded-md text-[10px] flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span> GPU-ACCELERATED
              </div>
              <div className="px-3 py-1 bg-white/5 border border-white/10 backdrop-blur-md rounded-md text-[10px] flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span> VERTEX-AI 2.0
              </div>
           </div>
        </div>
        
        <div className="text-[10px] uppercase tracking-widest text-white/20 text-right font-light">
          Built for the next generation of<br/>
          <span className="text-white/40 font-bold">Scientific Inquiry</span>
        </div>
      </footer>

      {showSummaryModal && (
        <SummaryModal 
          summary={summaryText} 
          onClose={() => setShowSummaryModal(false)} 
        />
      )}

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes nod {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-15px); }
        }
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-10px); }
          75% { transform: translateX(10px); }
        }
        @keyframes progress {
          0% { width: 0%; }
          100% { width: 100%; }
        }
        .nod-animation { animation: nod 0.5s ease-in-out 2; }
        .shake-animation { animation: shake 0.5s ease-in-out 2; }
        .perspective-1000 { perspective: 1000px; }
        .preserve-3d { transform-style: preserve-3d; }
        .scrollbar-thin::-webkit-scrollbar { width: 4px; }
        .scrollbar-thin::-webkit-scrollbar-track { background: rgba(255,255,255,0.05); }
        .scrollbar-thin::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 10px; }
        .markdown-content p { margin-bottom: 0.5rem; }
        .markdown-content code { background: rgba(0,0,0,0.3); padding: 0.1rem 0.3rem; border-radius: 4px; font-family: monospace; }
      `}} />
    </div>
  );
};

export default AnimatedAvatar;