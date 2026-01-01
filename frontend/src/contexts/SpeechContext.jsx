import React, { createContext, useContext, useState, useRef, useCallback, useEffect } from 'react';
import { generateSpeechFromText } from '../api/media';

const SpeechContext = createContext();

export const SpeechProvider = ({ children }) => {
  console.log("DELTA: SpeechProvider rendering");
  const [isListening, setIsListening] = useState(false);
  const [isTalking, setIsTalking] = useState(false);
  const recognition = useRef(null);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      console.log("DELTA: Speech recognition system initialized.");
      recognition.current = new SpeechRecognition();
      recognition.current.continuous = false;
      recognition.current.interimResults = false;
      recognition.current.lang = "en-US";
    } else {
      console.warn("DELTA: Speech recognition not supported in this browser.");
    }
  }, []);

  const startListening = useCallback((onResult, onError) => {
    if (!recognition.current) {
      console.error("DELTA: Cannot start listening - recognition not initialized.");
      return;
    }

    recognition.current.onresult = (event) => {
      const text = event.results[0][0].transcript;
      console.log("DELTA: Speech result received:", text);
      onResult(text);
      setIsListening(false);
    };

    recognition.current.onerror = (event) => {
      console.error("DELTA: Speech recognition error:", event.error);
      setIsListening(false);
      if (onError) onError(event.error);
    };

    recognition.current.onend = () => {
      setIsListening(false);
    };

    setIsListening(true);
    recognition.current.start();
  }, []);

  const speak = useCallback(async (text) => {
    if (!text || text.trim() === "") {
      console.log("DELTA: Skipping speech synthesis for empty text.");
      return;
    }
    console.log("DELTA: Synthesizing speech for:", text.substring(0, 50) + "...");
    try {
      const audioContent = await generateSpeechFromText(text);
      if (audioContent) {
        console.log("DELTA: Audio generated successfully, playing...");
        return new Promise((resolve) => {
          const audio = new Audio('data:audio/mp3;base64,' + audioContent);
          setIsTalking(true);
          audio.onended = () => {
            console.log("DELTA: Audio playback ended.");
            setIsTalking(false);
            resolve();
          };
          audio.onerror = (e) => {
            console.error("DELTA: Audio playback error:", e);
            setIsTalking(false);
            resolve();
          };
          audio.play().catch((e) => {
            console.error('DELTA: Autoplay prevented or failed:', e);
            setIsTalking(false);
            resolve();
          });
        });
      } else {
        console.error("DELTA: No audio content received from backend.");
        setIsTalking(false);
      }
    } catch (error) {
      console.error('DELTA: Speech synthesis error:', error);
      setIsTalking(false);
    }
  }, []);

  const value = {
    isListening,
    isTalking,
    startListening,
    speak,
    setIsTalking
  };

  return (
    <SpeechContext.Provider value={value}>
      {children}
    </SpeechContext.Provider>
  );
};

export const useSpeech = () => {
  const context = useContext(SpeechContext);
  if (!context) {
    throw new Error('useSpeech must be used within a SpeechProvider');
  }
  return context;
};
