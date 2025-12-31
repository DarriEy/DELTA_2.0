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
  
  const { isListening, isTalking, startListening, speak } = useSpeech();
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
      console.log("DELTA: Initializing core systems...");
      
      try {
        // 1. Establish Secure Neural Link (Conversation)
        let convId = currentConversationId;
        if (!convId) {
          console.log("DELTA: Creating new secure conversation...");
          convId = await createNewConversation('general');
        }

        // 2. Render Initial Environment (Background)
        if (convId) {
          const imagePrompt = 'Please, render a highly detailed photorealistic, 4K image of a natural landscape showcasing a beautiful hydrological landscape feature. The setting should be a breathtaking natural environment. Emphasize realistic lighting, textures, and reflections in the water. Style should render with sharp focus and intricate details. Use a 16:9 aspect ratio.';
          console.log("DELTA: Generating environmental background...");
          generateBackground('general', imagePrompt);
        }
        
      } catch (err) {
        console.error("DELTA: Initialization failure:", err);
      }
    };
    init();
  }, []);

  // Update animations based on talking state
  useEffect(() => {
    setIsNodding(isTalking);
  }, [isTalking]);

  const handleAvatarClick = async () => {
    console.log("DELTA: Avatar clicked. State:", { introductionSpoken, isListening, isTalking });
    
    if (!introductionSpoken) {
      const greeting = "Hi I'm Delta, your personal hydrological research assistant. How should we save the world today?";
      console.log("DELTA: Speaking introduction...");
      try {
        await speak(greeting);
        setIntroductionSpoken(true);
        // Automatically start listening after greeting
        console.log("DELTA: Greeting finished, starting to listen...");
        startListening(handleSpeechRecognitionResult, (error) => {
          console.error(`Speech recognition error: ${error}`);
          setIsShaking(true);
          setTimeout(() => setIsShaking(false), 1000);
        });
      } catch (err) {
        console.error("DELTA: Speech failed:", err);
      }
    } else if (!isListening && !isTalking) {
      console.log("DELTA: Starting speech recognition...");
      startListening(handleSpeechRecognitionResult, (error) => {
        console.error(`Speech recognition error: ${error}`);
        setIsShaking(true);
        setTimeout(() => setIsShaking(false), 1000);
      });
    }
  };

  const handleSpeechRecognitionResult = async (text) => {
    if (!text) return;
    setIsProcessing(true);
    try {
      const llmResponse = await sendMessage(text);
      if (llmResponse) {
         await speak(llmResponse);
         // Automatically listen again after Delta finishes talking
         if (!isListening) {
           startListening(handleSpeechRecognitionResult);
         }
      }
    } catch (error) {
      console.error(error);
      setIsShaking(true);
      setTimeout(() => setIsShaking(false), 1000);
    } finally {
      setIsProcessing(false);
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
      setIsShaking(true);
      setTimeout(() => setIsShaking(false), 1000);
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
      className="min-h-screen w-screen flex flex-col items-center justify-center font-sans text-white selection:bg-blue-500/30 transition-all duration-1000 bg-slate-950"
      style={{
        background: getBackground()?.startsWith('data:') || getBackground()?.startsWith('http') 
          ? `radial-gradient(circle at center, rgba(15,23,42,0.4) 0%, rgba(2,6,23,1) 100%), url(${getBackground()}) center/cover no-repeat` 
          : getBackground() || 'linear-gradient(135deg, #020617 0%, #0f172a 100%)',
      }}
    >
      
      {/* HUD Header */}
      <header className="absolute top-0 left-0 right-0 z-30 px-12 py-10 flex justify-between items-center pointer-events-none">
        <div className="flex items-center gap-6 pointer-events-auto group">
          <div className="relative">
             <div className="absolute inset-0 bg-blue-500 blur-2xl opacity-20 group-hover:opacity-40 transition-opacity"></div>
             <div className="w-16 h-16 rounded-2xl bg-white/5 backdrop-blur-3xl border border-white/10 flex items-center justify-center overflow-hidden shadow-2xl relative z-10">
                <img src={dropletAvatar} alt="Logo" className="w-10 h-10 object-contain" />
             </div>
          </div>
          <div>
            <h1 className="text-3xl font-black tracking-tighter text-white drop-shadow-2xl uppercase italic">
              DELTA <span className="text-blue-500 not-italic font-light">2.0</span>
            </h1>
            <div className="flex items-center gap-2">
               <div className="h-[1px] w-4 bg-blue-500/50"></div>
               <span className="text-[10px] font-bold text-white/30 uppercase tracking-[0.4em]">Integrated Intelligence Node</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-8 pointer-events-auto">
           <div className="flex flex-col items-end">
              <span className="text-xs font-black text-blue-400">DEC 30 2025</span>
              <span className="text-[10px] text-white/30 font-mono tracking-widest uppercase">Nodes Online</span>
           </div>
        </div>
      </header>

      <ModeSelector onSwitchMode={switchMode} onGetSummary={handleGetSummary} />

      <main className="z-10 w-full max-w-[1400px] px-12 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
        
        {/* Left: Avatar Display */}
        <div className="lg:col-span-5 flex justify-center">
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

        {/* Right: Functional HUD */}
        <div className="lg:col-span-7 space-y-8 h-[700px] flex flex-col justify-center">
          <div className="grid grid-cols-1 gap-8 h-full py-12">
            
            {/* Upper: Chat Stream */}
            <ChatPanel />

            {/* Lower: Dynamic Workspace */}
            <div className={`transition-all duration-700 h-full ${showContentFrame ? 'opacity-100 translate-y-0' : 'opacity-60 translate-y-4 pointer-events-none grayscale blur-sm'}`}>
              <div className="h-full bg-slate-900/40 backdrop-blur-3xl border border-white/5 rounded-[2rem] p-10 overflow-y-auto scrollbar-hide">
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
                  <div className="h-full flex flex-col items-center justify-center text-center space-y-8 animate-in fade-in zoom-in duration-1000">
                    <div className="relative">
                       <div className="absolute inset-0 bg-blue-500 blur-3xl opacity-10 animate-pulse"></div>
                       <div className="w-24 h-24 bg-white/5 border border-white/10 rounded-[2rem] flex items-center justify-center text-5xl relative z-10 shadow-2xl">🌍</div>
                    </div>
                    <div className="space-y-4">
                       <h4 className="text-4xl font-black text-white tracking-tighter uppercase italic">Welcome Commander</h4>
                       <p className="max-w-md mx-auto text-sm text-white/40 leading-relaxed tracking-wide font-light">
                         Delta is standing by. Access specialized hydrological nodes via the primary navigation interface on the left.
                       </p>
                    </div>
                  </div>
                )}
              </div>
            </div>

          </div>
        </div>
      </main>

      {/* Footer / Telemetry */}
      <footer className="absolute bottom-10 left-12 right-12 z-20 flex justify-between items-end pointer-events-none">
        <div className="flex flex-col gap-4 pointer-events-auto">
           <div className="flex gap-6">
              {[
                { label: 'Compute', value: '42.8 TFLOPS' },
                { label: 'Latency', value: '14ms' },
                { label: 'Model', value: 'Gemini-2.0' }
              ].map((stat, i) => (
                <div key={i} className="px-5 py-3 bg-white/5 border border-white/10 backdrop-blur-md rounded-2xl flex flex-col">
                  <span className="text-[8px] uppercase font-bold text-white/20 mb-1">{stat.label}</span>
                  <span className="text-xs font-mono font-black text-white/80">{stat.value}</span>
                </div>
              ))}
           </div>
        </div>
        
        <div className="text-right pointer-events-auto">
          <p className="text-[9px] uppercase tracking-[0.4em] text-white/20 font-light leading-relaxed">
            Proprietary Intelligence Core<br/>
            <span className="text-white/60 font-black">HYDROLOGICAL RESEARCH UNIT</span>
          </p>
        </div>
      </footer>

      {showSummaryModal && <SummaryModal summary={summaryText} onClose={() => setShowSummaryModal(false)} />}

      <style dangerouslySetInnerHTML={{ __html: `
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
      `}} />
    </div>
  );
};

export default AnimatedAvatar;