import React, { useState, useEffect, useRef } from "react";
import { generateSpeechFromText, generateImageFromPrompt } from "./services";
import educationalContent from "./educationalContent.json";
import modelingContent from "./modelingContent.json";
import dataAnalysisContent from "./dataAnalysisContent.json";
import SummaryModal from './summaryModal';
import dropletAvatar from './assets/Droplet_avatar.png';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

const GlassCard = ({ children, className = "" }) => (
  <div className={`glass-card p-6 ${className}`}>
    {children}
  </div>
);

const AnimatedAvatar = () => {
  // State
  const [isNodding, setIsNodding] = useState(false);
  const [isShaking, setIsShaking] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isTalking, setIsTalking] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [introductionSpoken, setIntroductionSpoken] = useState(false);
  
  // Content & Mode State
  const [activeMode, setActiveMode] = useState('general');
  const [showContentFrame, setShowContentFrame] = useState(false);
  
  // Backgrounds
  const [generalBackgroundImageUrl, setGeneralBackgroundImageUrl] = useState(null);
  const [backgroundImageUrl, setBackgroundImageUrl] = useState(null); // Educational
  const [backgroundImageModeling, setBackgroundImageModeling] = useState(null);
  const [backgroundImageDataAnalysis, setBackgroundImageDataAnalysis] = useState(null);

  // Data State
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [conversationHistory, setConversationHistory] = useState([]);
  const [selectedModel, setSelectedModel] = useState("SUMMA");
  const [selectedVariable, setSelectedVariable] = useState("temperature");
  const [summaryText, setSummaryText] = useState("");
  const [showSummaryModal, setShowSummaryModal] = useState(false);
  const [jobStatus, setJobStatus] = useState(null); // Add jobStatus state
  const [jobResult, setJobResult] = useState(null); // Add jobResult state
  const [jobLogs, setJobLogs] = useState(""); // Add jobLogs state

  // Content Data
  const [currentEducationalContent, setCurrentEducationalContent] = useState(null);
  const [currentModelingContent, setCurrentModelingContent] = useState(null);
  const [currentDataAnalysisContent, setCurrentDataAnalysisContent] = useState(null);

  const API_BASE_URL = import.meta.env.VITE_APP_API_BASE_URL || 'https://delta-backend-zom0.onrender.com';
  const avatarRef = useRef(null);
  const recognition = useRef(null);

  // --- Initial Setup ---
  useEffect(() => {
    generateGeneralBackgroundImage();
    initSpeechRecognition();
  }, []);

  const initSpeechRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognition.current = new SpeechRecognition();
      recognition.current.continuous = false;
      recognition.current.interimResults = false;
      recognition.current.lang = "en-US";

      recognition.current.onresult = (event) => {
        const text = event.results[0][0].transcript;
        console.log("Speech recognition result:", text);
        handleSpeechRecognitionResult(text);
      };

      recognition.current.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
        setIsListening(false);
        setIsProcessing(false);
      };

      recognition.current.onend = () => {
        setIsListening(false);
        setIsProcessing(false);
      };
    }
  };

  const generateGeneralBackgroundImage = async () => {
    // Give the UI a brief moment before generating a background. A shorter
    // delay improves perceived responsiveness on first load. Use a default
    // fallback image if no image is returned from the backend.
    await new Promise((resolve) => setTimeout(resolve, 1000));
    const imagePrompt =
      'Please, render a highly detailed photorealistic, 4K image of a natural landscape showcasing a beautiful hydrological landscape feature. The setting should be a breathtaking natural environment. Emphasize realistic lighting, textures, and reflections in the water. Style should render with sharp focus and intricate details. Use a 16:9 aspect ratio.';
    try {
      setIsLoading(true);
      const imageUrl = await generateImageFromPrompt(imagePrompt);
      if (imageUrl) {
        setGeneralBackgroundImageUrl(imageUrl);
      } else {
        console.warn('Falling back to default general background');
        // optional: set a fallback background image here if available
      }
    } catch (error) {
      console.error('Error generating background:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // --- Core Logic ---

  const createNewConversation = async (mode) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/conversations/`, {
        method: "POST",
        credentials: 'include',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ active_mode: mode, user_id: 1 }),
      });
      if (!response.ok) throw new Error("Failed to create conversation");
      const data = await response.json();
      setCurrentConversationId(data.conversation_id);
      return data.conversation_id;
    } catch (error) {
      console.error(error);
      return null;
    }
  };

  const handleSpeechRecognitionResult = async (text) => {
    if (!text) return;
    setIsListening(false);
    setIsTalking(true); // Temporary visual feedback
    setIsLoading(true);

    const updatedHistory = [...conversationHistory, { role: "user", content: text }];
    setConversationHistory(updatedHistory);

    try {
      let conversationId = currentConversationId;
      if (!conversationId) {
        conversationId = await createNewConversation(activeMode);
        if (!conversationId) return;
        await new Promise((resolve) => setTimeout(resolve, 200));
      }

      let apiEndpoint = activeMode === 'educational' ? "/api/learn" : "/api/process";
      const llmResponse = await sendToLLM(updatedHistory, apiEndpoint, conversationId);

      if (llmResponse) {
         setConversationHistory(prev => [...prev, { role: "assistant", content: llmResponse }]);
         await speak(llmResponse);
      }

    } catch (error) {
      console.error(error);
      alert("Error processing request.");
    } finally {
      setIsTalking(false);
      setIsProcessing(false);
      setIsLoading(false);
    }
  };

  const sendToLLM = async (history, endpoint, conversationId) => {
    const lastMessage = history[history.length - 1];
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "POST",
        credentials: 'include',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_input: lastMessage.content,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) throw new Error("LLM API Error");
      const data = await response.json();
      return data.llmResponse;
    } catch (error) {
      console.error("LLM Error:", error);
      return null;
    }
  };

  const speak = async (text) => {
    try {
      setIsLoading(true);
      const audioContent = await generateSpeechFromText(text);
      return new Promise((resolve) => {
        if (audioContent) {
          const audio = new Audio('data:audio/mp3;base64,' + audioContent);
          setIsTalking(true);
          // Attempt to play audio. If autoplay is prevented by the browser,
          // catch and log the error but continue to resolve the promise.
          audio.play().catch((e) => console.error('Autoplay prevented:', e));
          audio.onended = () => {
            setIsTalking(false);
            resolve();
          };
          audio.onerror = (e) => {
            console.error('Audio playback error:', e);
            setIsTalking(false);
            resolve();
          };
        } else {
          // If no audio content is returned, skip playback but still
          // resolve to avoid rejecting the promise and halting the chain.
          console.warn('No audio content received for speech synthesis');
          setIsTalking(false);
          resolve();
        }
      });
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const startListening = () => {
    if (recognition.current && !isListening && !isProcessing) {
      try {
        setIsProcessing(true);
        setIsListening(true);
        recognition.current.start();
      } catch (e) {
        console.error(e);
      }
    }
  };

  const handleAvatarClick = async () => {
    if (!introductionSpoken) {
      const textToSpeak = "Hi I'm Delta, your personal hydrological research assistant. How should we save the world today?";
      try {
        setIsLoading(true);
        await speak(textToSpeak);
        setIntroductionSpoken(true);
      } catch (error) {
        console.error(error);
      } finally {
        setIsLoading(false);
      }
    } else if (!isListening) {
      startListening();
    }
  };

  // --- Mode Handling ---

  const switchMode = async (mode) => {
    if (activeMode === mode) return; // Already active
    
    // Reset content specific state
    setShowContentFrame(false); 
    setActiveMode(mode);

    // Logic to fetch background/content based on mode
    if (mode === 'educational') {
      setCurrentEducationalContent(educationalContent.hydrology101);
      if (!backgroundImageUrl) {
        setIsLoading(true);
        const prompt =
          'Please generate a photorealistic image of a university classroom from the perspective of a student...';
        try {
          const url = await generateImageFromPrompt(prompt);
          if (url) {
            setBackgroundImageUrl(url);
          } else {
            console.warn('Falling back to default educational background');
          }
        } catch (e) {
          console.error('Error generating educational background:', e);
        } finally {
          setIsLoading(false);
        }
      }
      setShowContentFrame(true);
    } else if (mode === 'modeling') {
      setCurrentModelingContent(modelingContent.intro);
      if (!backgroundImageModeling) {
        setIsLoading(true);
        const prompt =
          'Please create a photorealistic image of the interior of an advanced hydrological monitoring space...';
        try {
          const url = await generateImageFromPrompt(prompt);
          if (url) {
            setBackgroundImageModeling(url);
          } else {
            console.warn('Falling back to default modeling background');
          }
        } catch (e) {
          console.error('Error generating modeling background:', e);
        } finally {
          setIsLoading(false);
        }
      }
      setShowContentFrame(true);
    } else if (mode === 'dataAnalysis') {
      setCurrentDataAnalysisContent(dataAnalysisContent.intro);
      if (!backgroundImageDataAnalysis) {
        setIsLoading(true);
        const prompt =
          'Please generate a photorealistic, top-down view of a modern, hydrological data analysis idea board...';
        try {
          const url = await generateImageFromPrompt(prompt);
          if (url) {
            setBackgroundImageDataAnalysis(url);
          } else {
            console.warn('Falling back to default data analysis background');
          }
        } catch (e) {
          console.error('Error generating data analysis background:', e);
        } finally {
          setIsLoading(false);
        }
      }
      setShowContentFrame(true);
    } else {
      // General
      setShowContentFrame(false);
    }
  };

  const handleEndOfDay = async () => {
    if (!currentConversationId) return alert("No conversation to summarize.");
    try {
        const response = await fetch(`${API_BASE_URL}/api/summary/${currentConversationId}`);
        if (!response.ok) throw new Error("Failed to get summary");
        const data = await response.json();
        setSummaryText(data.summary);
        setShowSummaryModal(true);
    } catch (e) {
        console.error(e);
        alert(e.message);
    }
  };

  const handleRunModels = async (jobType = "SIMULATION") => {
    console.log(`Running ${jobType} for:`, selectedModel);
    setIsLoading(true);
    setJobStatus("Submitting...");
    setJobResult(null);
    setJobLogs("Initiating connection to local runner...");
  
    try {
      const response = await fetch(`${API_BASE_URL}/api/run_modeling`, {
        method: "POST",
        credentials: 'include',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
            model: selectedModel,
            job_type: jobType 
        }),
      });
  
      if (!response.ok) throw new Error("Failed to submit job");
  
      const result = await response.json();
      const jobId = result.job_id;
      setJobStatus("Queued");
      
      // Poll for job status
      const pollJob = setInterval(async () => {
          try {
              const statusRes = await fetch(`${API_BASE_URL}/api/jobs/${jobId}`);
              if (statusRes.ok) {
                  const job = await statusRes.json();
                  setJobStatus(job.status);
                  if (job.logs) setJobLogs(job.logs); // Update logs in real-time

                  if (job.status === 'COMPLETED' || job.status === 'FAILED') {
                      clearInterval(pollJob);
                      setIsLoading(false);
                      if (job.status === 'COMPLETED') {
                          setJobResult(job.result);
                          await speak("The task is complete. You can see the results and execution logs on your screen.");
                      } else {
                          await speak("I encountered an error during execution.");
                      }
                  }
              }
          } catch (e) {
              console.error("Polling error:", e);
          }
      }, 2000);

    } catch (error) {
      console.error("Error running modeling:", error);
      setJobLogs(prev => prev + `\n[UI ERROR] Failed to connect to server: ${error.message}\nPossible causes: Backend is asleep, CORS error, or Internet connection lost.`);
      alert("Failed to start modeling. Check the console logs for details.");
      setIsLoading(false);
      setJobStatus(null);
    }
  };

   const handleRunAnalysis = () => {
      setIsLoading(true);
      setTimeout(() => {
          setIsLoading(false);
          alert(`Data analysis for ${selectedVariable} complete.`);
      }, 2000);
  };


  // --- Render Helpers ---

  const getActiveBackground = () => {
    switch (activeMode) {
        case 'educational': return backgroundImageUrl;
        case 'modeling': return backgroundImageModeling;
        case 'dataAnalysis': return backgroundImageDataAnalysis;
        default: return generalBackgroundImageUrl;
    }
  };

  return (
    <div className="relative w-full h-screen overflow-hidden bg-slate-900 font-sans text-slate-100">
      
      {/* 1. Dynamic Background */}
      <div 
        className="absolute inset-0 z-0 bg-cover bg-center transition-all duration-1000 ease-in-out bg-transition"
        style={{ backgroundImage: `url(${getActiveBackground()})` }}
      />
      
      {/* Overlay Gradient */}
      <div className="absolute inset-0 z-0 bg-gradient-to-t from-black/80 via-black/40 to-black/30 pointer-events-none" />

      {/* 2. Top Navigation Bar */}
      <div className="absolute top-0 left-0 w-full p-6 flex justify-between items-center z-50">
          <div className="flex items-center gap-3">
             <div className="w-8 h-8 rounded-full bg-cyan-500 blur-sm animate-pulse-glow" />
             <h1 className="text-2xl font-bold tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 drop-shadow-lg">
                 DELTA <span className="text-xs font-light tracking-widest text-white/60 ml-1">v2.0</span>
             </h1>
          </div>
          
          <button 
            onClick={handleEndOfDay}
            className="glass-button bg-red-500/20 hover:bg-red-500/40 border-red-500/30 text-red-100 text-sm font-semibold"
          >
             End Session
          </button>
      </div>

      {/* 3. Main Content Area */}
      <div className="relative z-10 w-full h-full flex items-center justify-center">
        
        {/* AVATAR SECTION */}
        <div className={`flex flex-col items-center transition-all duration-700 ${showContentFrame ? 'mr-[500px] scale-90' : 'scale-110'}`}>
            
            {/* Start Hint */}
            {!introductionSpoken && !isLoading && (
              <div className="mb-4 px-4 py-2 bg-white/10 backdrop-blur rounded-full border border-white/20 text-cyan-300 text-sm font-semibold animate-bounce">
                Tap to wake me up
              </div>
            )}

            {/* Avatar Interaction Zone */}
            <div 
                className="relative cursor-pointer group"
                onClick={handleAvatarClick}
                onDoubleClick={() => setIsShaking(true)}
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
            >
                {/* Listening Aura */}
                {isListening && (
                    <div className="absolute inset-0 bg-cyan-500/30 blur-2xl animate-liquid z-0" />
                )}
                
                {/* Loading Spinner */}
                {isLoading && (
                     <div className="absolute -inset-4 border-t-4 border-cyan-400 rounded-full animate-spin z-20" />
                )}

                {/* The Droplet */}
                <img 
                    src={dropletAvatar} 
                    alt="Delta" 
                    className={
                        `
                        relative z-10 w-64 h-64 object-contain drop-shadow-2xl transition-transform duration-300
                        ${isTalking ? 'animate-talking' : 'animate-float'}
                        ${isShaking ? 'animate-shake' : ''}
                        ${isHovered ? 'scale-105 brightness-110' : ''}
                    `}
                />
            </div>

            {/* Status Indicator */}
            <div className="mt-8 flex items-center gap-2 px-4 py-1.5 rounded-full bg-black/40 backdrop-blur border border-white/10">
                <div className={`w-2 h-2 rounded-full ${isListening ? 'bg-red-500 animate-pulse' : isTalking ? 'bg-green-500 animate-pulse' : isLoading ? 'bg-yellow-400 animate-spin' : 'bg-cyan-500'}`} />
                <span className="text-xs font-medium tracking-wide uppercase text-white/70">
                    {jobStatus ? `Job: ${jobStatus}` : isListening ? "Listening..." : isTalking ? "Speaking..." : isLoading ? "Thinking..." : "Ready"}
                </span>
            </div>
        </div>

        {/* SIDE CONTENT PANEL (Glass Card) */}
        {showContentFrame && (
            <div className="absolute right-8 top-1/2 -translate-y-1/2 w-[450px] max-h-[80vh] overflow-y-auto glass-card animate-fadeIn flex flex-col">
                 {/* Close Button */}
                 <button onClick={() => setActiveMode('general')} className="absolute top-4 right-4 text-white/50 hover:text-white z-20">✕</button>

                 <div className="flex-1 p-2 overflow-y-auto custom-scrollbar">
                    {/* Chat History for Scientific Rigor */}
                    <div className="space-y-4 mb-6">
                        {conversationHistory.map((msg, idx) => (
                            <div key={idx} className={`p-3 rounded-xl ${msg.role === 'user' ? 'bg-white/10 ml-8' : 'bg-cyan-900/20 mr-8 border border-cyan-500/20'}`}>
                                <div className="text-[10px] uppercase tracking-widest text-white/40 mb-1 font-bold">
                                    {msg.role === 'user' ? 'Researcher' : 'DELTA'}
                                </div>
                                <div className="text-sm prose prose-invert max-w-none">
                                    <ReactMarkdown 
                                        remarkPlugins={[remarkMath]} 
                                        rehypePlugins={[rehypeKatex]}
                                    >
                                        {msg.content}
                                    </ReactMarkdown>
                                </div>
                            </div>
                        ))}
                    </div>

                 {/* Dynamic Content */}
                 {activeMode === 'educational' && currentEducationalContent && (
                    <div className="space-y-4">
                        <h2 className="text-2xl font-bold text-cyan-400">{currentEducationalContent.title}</h2>
                        <p className="text-sm text-slate-300 leading-relaxed">{currentEducationalContent.overview}</p>
                        
                        <div className="bg-white/5 rounded-xl p-4 border border-white/10">
                            <h3 className="text-sm font-bold uppercase tracking-wider text-cyan-200 mb-3">Syllabus</h3>
                            <ul className="space-y-3">
                                {currentEducationalContent.topics.map((t, i) => (
                                    <li key={i} className="text-xs text-slate-300 flex flex-col">
                                        <span className="font-semibold text-white">{t.name}</span>
                                        <span className="opacity-70">{t.description}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                 )}

                 {activeMode === 'modeling' && currentModelingContent && (
                    <div className="space-y-4">
                        <h2 className="text-2xl font-bold text-blue-400">{currentModelingContent.title}</h2>
                        
                        {jobResult && jobResult.plot_base64 && (
                            <div className="mt-4 rounded-xl overflow-hidden border border-white/20 shadow-2xl bg-black/20">
                                <img 
                                    src={`data:image/png;base64,${jobResult.plot_base64}`} 
                                    alt="Result Plot" 
                                    className="w-full h-auto"
                                />
                            </div>
                        )}

                        {/* Terminal Console */}
                        {jobStatus && (
                            <div className="mt-4 rounded-xl border border-white/10 bg-black/60 shadow-inner overflow-hidden flex flex-col h-[200px]">
                                <div className="bg-white/5 px-3 py-1 border-b border-white/10 flex justify-between items-center">
                                    <span className="text-[10px] uppercase tracking-widest text-white/40 font-bold">Execution Logs</span>
                                    <div className="flex gap-1.5">
                                        <div className="w-2 h-2 rounded-full bg-red-500/50" />
                                        <div className="w-2 h-2 rounded-full bg-yellow-500/50" />
                                        <div className="w-2 h-2 rounded-full bg-green-500/50" />
                                    </div>
                                </div>
                                <div className="p-3 overflow-y-auto font-mono text-[10px] leading-relaxed text-cyan-100/80 whitespace-pre-wrap">
                                    {jobLogs || "Waiting for output..."}
                                    {jobStatus === 'RUNNING' && <span className="inline-block w-1.5 h-3 ml-1 bg-cyan-400 animate-pulse align-middle" />}
                                </div>
                            </div>
                        )}

                        <div className="glass-panel p-4 rounded-xl">
                            <label className="text-xs uppercase font-bold text-blue-200 block mb-2">Select Hydrological Model</label>
                            <select 
                                value={selectedModel} 
                                onChange={(e) => setSelectedModel(e.target.value)}
                                className="w-full bg-black/50 border border-white/20 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                            >
                                {["SUMMA", "FUSE", "GR", "NGEN"].map(m => <option key={m} value={m}>{m}</option>)}
                            </select>
                        </div>
                        
                        <div className="flex gap-2">
                            <button onClick={() => handleRunModels("SIMULATION")} className="flex-1 glass-button bg-blue-600/30 hover:bg-blue-600/50 text-xs">
                                Run Simulation
                            </button>
                            <button onClick={() => handleRunModels("CALIBRATION")} className="flex-1 glass-button bg-orange-600/30 hover:bg-orange-600/50 text-xs">
                                Calibrate Model
                            </button>
                        </div>
                    </div>
                 )}

                 {activeMode === 'dataAnalysis' && currentDataAnalysisContent && (
                    <div className="space-y-4">
                        <h2 className="text-2xl font-bold text-purple-400">{currentDataAnalysisContent.title}</h2>
                        <p className="text-sm text-slate-300">{currentDataAnalysisContent.overview}</p>
                         
                          <div className="glass-panel p-4 rounded-xl">
                              <label className="text-xs uppercase font-bold text-purple-200 block mb-2">Target Variable</label>
                              <select 
                                  value={selectedVariable} 
                                  onChange={(e) => setSelectedVariable(e.target.value)}
                                  className="w-full bg-black/50 border border-white/20 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-purple-500"
                              >
                                  <option value="temperature">Temperature</option>
                                  <option value="precipitation">Precipitation</option>
                              </select>
                          </div>
                          <button onClick={handleRunAnalysis} className="w-full glass-button bg-purple-600/30 hover:bg-purple-600/50">
                              Analyze Dataset
                          </button>
                    </div>
                 )}
                 </div>
            </div>
        )}

      </div>

      {/* 4. Bottom Dock Navigation */}
      <div className="dock-container">
          {[
              { id: 'general', label: 'General', color: 'hover:shadow-cyan-500/50 hover:bg-cyan-500/20' },
              { id: 'educational', label: 'Learn', color: 'hover:shadow-green-500/50 hover:bg-green-500/20' },
              { id: 'modeling', label: 'Model', color: 'hover:shadow-blue-500/50 hover:bg-blue-500/20' },
              { id: 'dataAnalysis', label: 'Analyze', color: 'hover:shadow-purple-500/50 hover:bg-purple-500/20' },
          ].map((mode) => (
              <button
                key={mode.id}
                onClick={() => switchMode(mode.id)}
                className={
                    `
                        relative px-4 py-2 rounded-full transition-all duration-300
                        ${activeMode === mode.id ? 'bg-white/20 text-white shadow-[0_0_15px_rgba(255,255,255,0.3)] scale-110' : 'text-white/60 hover:text-white'}
                        ${mode.color}
                    `
                }
              >
                  <span className="text-sm font-medium">{mode.label}</span>
                  {activeMode === mode.id && (
                      <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-white" />
                  )}
              </button>
          ))}
      </div>

      {/* 5. Modals */}
      {showSummaryModal && (
        <SummaryModal 
            summary={summaryText} 
            onConfirm={() => { alert('Saved!'); setShowSummaryModal(false); }} 
            onCancel={() => setShowSummaryModal(false)} 
        />
      )}

    </div>
  );
};

export default AnimatedAvatar;
