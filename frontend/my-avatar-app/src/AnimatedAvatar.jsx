import React, { useState, useEffect, useRef } from "react";
import { generateSpeechFromText, generateImageFromPrompt } from "./services"; // Import from services.js
import educationalContent from "./educationalContent.json"; // Import educational content
import modelingContent from "./modelingContent.json";
import dataAnalysisContent from "./dataAnalysisContent.json";

const AnimatedAvatar = () => {
  const [isNodding, setIsNodding] = useState(false);
  const [isShaking, setIsShaking] = useState(false);
  const [isBouncing, setIsBouncing] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [showContentFrame, setShowContentFrame] = useState(false);
  const [glowOpacity, setGlowOpacity] = useState(0);
  const [backgroundImageUrl, setBackgroundImageUrl] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [isTalking, setIsTalking] = useState(false);
  const [selectedVariable, setSelectedVariable] = useState("temperature");
  const [showModelingContent, setShowModelingContent] = useState(false);
  const [showDataAnalysisContent, setShowDataAnalysisContent] = useState(false);
  const [activeMode, setActiveMode] = useState('general'); // Add activeMode state
  const [generalBackgroundImageUrl, setGeneralBackgroundImageUrl] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedModel, setSelectedModel] = useState("SUMMA"); // Add selectedModel state
  const [conversationHistory, setConversationHistory] = useState([]);
  const [showEducationalContent, setShowEducationalContent] = useState(false);
  const [currentEducationalContent, setCurrentEducationalContent] = useState(null);
  const [introductionSpoken, setIntroductionSpoken] = useState(false); // Track if introduction is spoken
  const [currentModelingContent, setCurrentModelingContent] = useState(null);
  const [currentDataAnalysisContent, setCurrentDataAnalysisContent] = useState(null);
  const [backgroundImageModeling, setBackgroundImageModeling] = useState(null);
  const [backgroundImageDataAnalysis, setBackgroundImageDataAnalysis] = useState(null);

  const [isLoading, setIsLoading] = useState(false); // Add a loading state
  const avatarRef = useRef(null);
  const recognition = useRef(null);

  // Pulsating glow on hover
  useEffect(() => {
    let intervalId;
    if (isHovered) {
      intervalId = setInterval(() => {
        setGlowOpacity((prevOpacity) => (prevOpacity === 0.2 ? 0.4 : 0.2));
      }, 500);
    } else {
      setGlowOpacity(0);
    }
    return () => clearInterval(intervalId);
  }, [isHovered]);

  // Shaking on double click
  const handleDoubleClick = () => {
    setIsShaking(true);
    setTimeout(() => setIsShaking(false), 300);
  };

  // Initialize Speech Recognition on component mount
  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
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
        // Display user-friendly error message
        alert(
          "Speech recognition error. Please check your microphone and try again."
        );
      };

      recognition.current.onend = () => {
        console.log("Speech recognition ended.");
        setIsListening(false);
        setIsProcessing(false);
      };
    } else {
      console.error("Speech recognition not supported");
      alert("Speech recognition is not supported in your browser.");
    }

    return () => {
      if (recognition.current) {
        recognition.current.stop();
      }
    };
  }, []);

  const generateGeneralBackgroundImage = async () => {
    const imagePrompt =
    "Please, render a highly detailed, 4K image of a natural landscape showcasing a: waterfall, river, stream, lake, glacier, or hot spring. The setting should be a breathtaking mountain range or a dense, lush forest. Capture the scene during the magical golden hour or the serene blue hour. Emphasize realistic lighting, textures, and reflections in the water. Style should render with sharp focus and intricate details. Use a 16:9 aspect ratio.";
    try {
      setIsLoading(true); // Start loading
      const imageUrl = await generateImageFromPrompt(imagePrompt);
      setGeneralBackgroundImageUrl(imageUrl);
    } catch (error) {
      console.error("Error generating general background image:", error);
      alert("Failed to generate background image. Please try again later.");
    } finally {
      setIsLoading(false); // End loading
    }
  };

  useEffect(() => {
    generateGeneralBackgroundImage();
  }, []);

  const startListening = () => {
    if (
      recognition.current &&
      !isListening &&
      !isProcessing
    ) {
      try {
        setIsProcessing(true);
        setIsListening(true);
        recognition.current.start();
        console.log("Speech recognition started.");
      } catch (error) {
        console.error("Error starting speech recognition:", error);
        setIsListening(false);
        setIsProcessing(false);
      }
    }
  };

  const stopListening = () => {
    if (recognition.current && isListening) {
      recognition.current.stop();
      console.log("Speech recognition stopped.");
    }
  };

  const handleModelSelection = (event) => {
    setSelectedModel(event.target.value);
  };

  const handleRunModels = async () => {
    console.log("Running model(s):", selectedModel);
    setIsLoading(true);

    // Prepare the model setting for the API request
    const modelSetting = selectedModel === "All of the above"
      ? "FUSE,GR,FLASH,SUMMA,HYPE,MESH"
      : selectedModel;

    try {
      // Make an API request to the backend to run CONFLUENCE
      const response = await fetch("http://localhost:8000/api/run_confluence", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: modelSetting,
          configPath: "/Users/darrieythorsson/compHydro/code/DELTA/backend/examples/config_Bow.yaml", // Update with your actual path
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to run CONFLUENCE");
      }

      const result = await response.json();
      console.log("CONFLUENCE run result:", result);

      // Handle the result, e.g., update state to show output or redirect to a results page
      alert(`Model(s) ${selectedModel} run completed.`);
    } catch (error) {
      console.error("Error running CONFLUENCE:", error);
      alert(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSpeechRecognitionResult = async (text) => {
    if (!text) {
      console.warn("Speech recognition result is empty or undefined.");
      return;
    }

    setIsListening(false);
    setIsTalking(true);
    setIsLoading(true); // Start loading

    const updatedHistory = [
      ...conversationHistory,
      { role: "user", content: text },
    ];
    setConversationHistory(updatedHistory);

    try {
      let apiEndpoint = showEducationalContent ? "/api/learn" : "/api/process";

      // Check if the last message is from the user
      if (updatedHistory[updatedHistory.length - 1].role !== "user") {
        console.error(
          "Last message in conversation history is not from the user"
        );
        alert("Please provide your input.");
        return;
      }

      const llmResponse = await sendToLLM(updatedHistory, apiEndpoint);

      if (llmResponse) {
        setConversationHistory([
          ...updatedHistory,
          { role: "assistant", content: llmResponse },
        ]);
        await speak(llmResponse);
      } else {
        console.warn("LLM response was undefined. Skipping speech.");
      }
    } catch (error) {
      console.error("Error handling speech recognition result:", error);
      alert("Error processing your request. Please try again.");
    } finally {
      setIsTalking(false);
      setIsProcessing(false);
      setIsLoading(false); // End loading
    }
  };

  const sendToLLM = async (conversationHistory, apiEndpoint) => {
    console.log("Conversation history:", conversationHistory);

    // Ensure the last message is from the user
    const lastMessage = conversationHistory[conversationHistory.length - 1];
    if (!lastMessage || lastMessage.role !== "user") {
      console.error(
        "Last message in conversation history is not from the user"
      );
      return;
    }

    const userMessage = lastMessage.content;
    console.log("Sending to LLM:", userMessage);

    // Retry mechanism with limit
    let retries = 0;
    const maxRetries = 3;
    let fullResponse = "";

    while (retries < maxRetries) {
      try {
        const response = await fetch(`http://localhost:8000${apiEndpoint}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ user_input: userMessage }),
        });

        console.log("LLM response status:", response.status);

        if (!response.ok) {
          console.error("HTTP error! status:", response.status);
          const errorBody = await response.text();
          console.error("Error body:", errorBody);
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log("LLM data:", data);

        const assistantResponse = data.llmResponse;
        if (!assistantResponse) {
          console.error("LLM response missing assistant text:", data);
          throw new Error("Assistant response text is missing");
        }

        fullResponse = assistantResponse;
        break; // Success, exit the loop
      } catch (error) {
        console.error(
          "Error in sendToLLM (attempt",
          retries + 1,
          "):",
          error
        );
        retries++;
        if (retries >= maxRetries) {
          console.error("Max retries reached. Aborting.");
          throw error; // Re-throw the error after max retries
        }
        // Optional: Implement a delay before the next retry
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
    }

    console.log("Full response from LLM:", fullResponse);
    return fullResponse;
  };

  const speak = async (text) => {
    try {
      setIsLoading(true); // Start loading
      const audioContent = await generateSpeechFromText(text);
      return new Promise((resolve, reject) => {
        console.log("Text to be spoken:", text);
        if (audioContent) {
          const audio = new Audio(
            "data:audio/mp3;base64," + audioContent
          );
          setIsTalking(true); // Start talking animation
          audio.play();
          audio.onended = () => {
            setIsTalking(false); // Stop talking animation
            resolve(); // Resolve the Promise when audio ends
          };
          audio.onerror = (error) => {
            console.error("Error playing audio:", error);
            setIsTalking(false); // Stop talking animation
            reject(error); // Reject the Promise on error
          };
        } else {
          throw new Error("No audio content received from TTS API");
        }
      });
    } catch (error) {
      console.error("Error during text-to-speech:", error);
      alert("Error generating speech. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleEducationalMode = async () => {
    setActiveMode(activeMode === "educational" ? "general" : "educational");
    setShowContentFrame(true);
  };

  const handleModelingMode = async () => {
    setActiveMode(activeMode === "modeling" ? "general" : "modeling");
    setShowContentFrame(true);
  };

  const handleDataAnalysisMode = async () => {
    setShowDataAnalysisContent(!showDataAnalysisContent);
    setActiveMode(showDataAnalysisContent ? "general" : "dataAnalysis");
    setShowContentFrame(!showDataAnalysisContent);

    if (showDataAnalysisContent) {
        setBackgroundImageDataAnalysis(null);
        setCurrentDataAnalysisContent(null);
    }
};

  const handleVariableSelection = (event) => {
    setSelectedVariable(event.target.value);
  };

  const handleRunAnalysis = () => {
    // This is where you will trigger the data analysis based on the selected variable
    console.log("Running analysis for:", selectedVariable);
    // Placeholder for now. Later, you'll integrate with your data analysis tools here.
    setIsLoading(true);

    // Simulate data analysis
    setTimeout(() => {
      setIsLoading(false);
      alert(
        `Data analysis for ${selectedVariable} in the Bow at Banff is complete (simulated).`
      );
    }, 3000);
  };



  useEffect(() => {
    const handleModeChange = async () => {
      if (activeMode === "general") {
        setShowContentFrame(false);
        setBackgroundImageUrl(null);
        setCurrentEducationalContent(null);
        setBackgroundImageModeling(null);
        setCurrentModelingContent(null);
        setBackgroundImageDataAnalysis(null);
        setCurrentDataAnalysisContent(null);
      } else if (activeMode === "educational") {
        const imagePrompt =
          "Generate a photorealistic image of a university classroom from the perspective of a student, with a 16:9 aspect ratio and 8K resolution. The main focus is a large, traditional chalkboard or whiteboard on the left, taking up most of the frame, ready for writing and diagrams. The classroom should have a fun, engaging atmosphere. Include various hydrological and geophysical items scattered around, such as a globe, a 3D model of a watershed, a rain gauge, a weather vane, rock samples, and posters of the water cycle and geological formations.  Add some fun, relevant memes related to hydrology and geophysics on the walls or desks. The lighting should be bright and welcoming, typical of an educational setting. The overall style should be realistic and detailed, capturing the essence of a lively and interactive learning environment.";
        try {
          setIsLoading(true);
          const imageUrl = await generateImageFromPrompt(imagePrompt);
          setBackgroundImageUrl(imageUrl);
          setCurrentEducationalContent(educationalContent.hydrology101);
          setShowContentFrame(true);
        } catch (error) {
          console.error("Error generating image or fetching content:", error);
          alert(
            "Failed to initialize educational mode. Please try again later."
          );
        } finally {
          setIsLoading(false);
        }
      } else if (activeMode === "modeling") {
        const imagePrompt =
          "Create a photorealistic image of the interior of an advanced hydrological monitoring space, rendered in 8K resolution with a 16:9 aspect ratio. The environment should evoke the feeling of being in a futuristic spaceship cockpit, without explicitly showing any spaceship elements.  Design the space with sleek, curved consoles, and large, high-resolution screens displaying complex hydrological models, real-time data streams, and dynamic 3D visualizations of water flow. Incorporate holographic projections of watersheds and river basins. The lighting should be a mix of soft, ambient glows from the screens and subtle, strategic accent lighting along the consoles. The overall atmosphere should be high-tech, immersive, and focused, as if in a command center for monitoring and analyzing complex environmental systems.";
        try {
          setIsLoading(true);
          const imageUrl = await generateImageFromPrompt(imagePrompt);
          setBackgroundImageModeling(imageUrl);
          setCurrentModelingContent(modelingContent.intro);
          setShowContentFrame(true);
        } catch (error) {
          console.error("Error generating image or fetching content:", error);
          alert("Failed to initialize modeling mode. Please try again later.");
        } finally {
          setIsLoading(false);
        }
      } else if (activeMode === "dataAnalysis") {
        const imagePrompt =
          "Generate a photorealistic, top-down view of a modern, hydrological data analysis idea board, 8K resolution. The central element is a large, empty canvas, ready for drawing and visualizations. Populate the board with various measurement tools and objects, such as digital calipers, rulers, protractors, data loggers, sensor readouts, and perhaps a disassembled flow meter. Include schematic diagrams of hydrological systems, printed charts of water levels and flow rates, and a scattering of writing utensils like pens, markers, and highlighters.  Arrange these elements as if on a large, well-lit worktable. The overall style should be highly detailed and realistic, as if captured by an overhead camera in a professional workspace. Use a 16:9 aspect ratio.";
        try {
          setIsLoading(true);
          const imageUrl = await generateImageFromPrompt(imagePrompt);
          setBackgroundImageDataAnalysis(imageUrl);
          setCurrentDataAnalysisContent(dataAnalysisContent.intro);
          setShowContentFrame(true);
        } catch (error) {
          console.error("Error generating image or fetching content:", error);
          alert(
            "Failed to initialize data analysis mode. Please try again later."
          );
        } finally {
          setIsLoading(false);
        }
      }
    };

    if (activeMode) {
      handleModeChange();
    }
  }, [activeMode]);


  const toggleContentFrame = () => {
    setShowContentFrame(!showContentFrame);
  };

  const handleAvatarClick = async () => {
    if (!introductionSpoken) {
      const textToSpeak =
        "Hi I'm Delta, your personal hydrological research assistant. How should we save the world today?";
      try {
        setIsLoading(true);
        await speak(textToSpeak);
        // Ensure setIntroductionSpoken is called before startListening
        setIntroductionSpoken(true);
      } catch (error) {
        console.error("Error during avatar speech:", error);
      } finally {
        setIsLoading(false);
      }
    } else if (!isListening) {
      startListening();
    }
  };

  useEffect(() => {
    // Start listening after introduction is fully spoken
    if (introductionSpoken && !isListening) {
      startListening();
    }
  }, [introductionSpoken, isListening]);


  // Toggle talking animation
  useEffect(() => {
    if (isTalking) {
      const talkingInterval = setInterval(() => {
        setIsTalking((prevIsTalking) => !prevIsTalking);
      }, 300);

      return () => clearInterval(talkingInterval);
    } else {
      setIsTalking(false);
    }
  }, [isTalking]);

  return (
    <div className="min-h-screen w-full overflow-hidden">
      <div 
        className="fixed inset-0 w-full h-full bg-cover bg-center bg-no-repeat"
        style={{
          backgroundImage: activeMode === "educational"
            ? `url(${backgroundImageUrl})`
            : activeMode === "modeling"
            ? `url(${backgroundImageModeling})`
            : activeMode === "dataAnalysis"
            ? `url(${backgroundImageDataAnalysis})`
            : generalBackgroundImageUrl
            ? `url(${generalBackgroundImageUrl})`
            : "none",
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat'
        }}
    >
              {/* Overlay to ensure content is visible */}
              <div className="absolute inset-0 bg-black bg-opacity-30">
          {/* Content container */}
          <div className="relative min-h-screen w-full flex flex-col items-center justify-start p-4">

          <div className="button-container absolute top-4 left-4">

        {/* Mode Buttons */}
        <button
          onClick={handleEducationalMode}
          className="ml-2 px-4 py-2 rounded bg-green-500 text-white"
        >
          {activeMode === "educational"
            ? "Back to General"
            : "Educational Mode"}
        </button>
        <button
          onClick={handleModelingMode}
          className="ml-2 px-4 py-2 rounded bg-blue-500 text-white"
        >
          {activeMode === "modeling" ? "Back to General" : "Modeling Mode"}
        </button>
        <button
          onClick={handleDataAnalysisMode}
          className="ml-2 px-4 py-2 rounded bg-purple-500 text-white"
        >
          {activeMode === "dataAnalysis"
            ? "Back to General"
            : "Data Analysis Mode"}
        </button>
            </div>

      <div
        className={`relative mt-20 avatar-container ${
          activeMode !== "general" ? "mode-change" : ""
        }`}
      >
        {/* Avatar code */}
        <div
          ref={avatarRef}
          className={`avatar-image-container relative transition-all duration-300 ease-in-out cursor-pointer
          ${isNodding ? "animate-nod" : ""}
          ${isShaking ? "animate-shake" : ""}
          ${isBouncing ? "animate-bounce" : ""}
          ${isHovered ? "scale-110 brightness-110" : "scale-100"}
          ${isTalking ? "talking animate-pulse-avatar" : ""}
          ${isListening ? "listening-glow" : ""}
        `}
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
          onClick={handleAvatarClick}
          onDoubleClick={handleDoubleClick}
        >
          {/* Loading Indicator (only show when loading) */}
          {isLoading && (
            <div className="animate-spin loading-ring rounded-full border-t-4 border-blue-500"></div>
          )}
          <img
            src="/Droplet_avatar.png"
            alt="Water drop avatar"
            className="object-contain avatar-image"
          />

          <div
            className={`absolute inset-0 rounded-full bg-blue-400 blur-xl transition-opacity duration-300`}
            style={{ opacity: glowOpacity }}
          />
        </div>
      </div>

      

{/* Content Frame */}
{(activeMode === "educational" ||
        activeMode === "modeling" ||
        activeMode === "dataAnalysis") && (
        <div
          className={`content-frame ${
            activeMode === "educational" ? "educational-mode" : ""
          }`}
        >
          <button
            onClick={() => setActiveMode("general")}
            className="close-content-button"
          >
            Close Content
          </button>
          {/* Display content based on active mode */}
          {activeMode === "educational" && currentEducationalContent && (
            <div>
              <h2>{currentEducationalContent.title}</h2>
              <p>{currentEducationalContent.overview}</p>
              <h3>Course Overview:</h3>
              <ul>
                {currentEducationalContent.topics.map((topic) => (
                  <li key={topic.name}>
                    <strong>{topic.name}:</strong> {topic.description}
                  </li>
                ))}
              </ul>
            </div>
          )}
            {activeMode === "modeling" && currentModelingContent && (
            <div>
              <h2>{currentModelingContent.title}</h2>
              <p>{currentModelingContent.overview}</p>
              <p>
                <b>Example:</b> Simulating the Bow River at Banff
              </p>
              <select
                value={selectedModel}
                onChange={handleModelSelection}
                className="model-select"
              >
                <option value="SUMMA">SUMMA</option>
                <option value="FUSE">FUSE</option>
                <option value="MESH">MESH</option>
                <option value="HYPE">HYPE</option>
                <option value="GR4J">GR4J</option>
                <option value="FLASH">FLASH</option>
                <option value="All of the above">All of the above</option>
              </select>
              <button onClick={handleRunModels} className="run-models-button">
                Run Model(s)
              </button>
            </div>
          )}
          {activeMode === "dataAnalysis" && currentDataAnalysisContent && (
            <div>
              <h2>{currentDataAnalysisContent.title}</h2>
              <p>{currentDataAnalysisContent.overview}</p>
              <p>
                <b>Example:</b> Estimating Average Daily Climate Variables in
                the Bow at Banff
              </p>
              <select
                value={selectedVariable}
                onChange={handleVariableSelection}
                className="variable-select"
              >
                <option value="temperature">Temperature</option>
                <option value="precipitation">Precipitation</option>
              </select>
              <button onClick={handleRunAnalysis} className="run-analysis-button">
                Run Analysis
              </button>
            </div>
          )}
        </div>
      )}
          </div>
          </div>
    </div>
    </div>
  );
};

export default AnimatedAvatar;