import { useState, useRef, useCallback, useEffect } from 'react';
import { generateSpeechFromText } from '../services';

export const useSpeech = () => {
  const [isListening, setIsListening] = useState(false);
  const [isTalking, setIsTalking] = useState(false);
  const recognition = useRef(null);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognition.current = new SpeechRecognition();
      recognition.current.continuous = false;
      recognition.current.interimResults = false;
      recognition.current.lang = "en-US";
    }
  }, []);

  const startListening = useCallback((onResult, onError) => {
    if (!recognition.current) return;

    recognition.current.onresult = (event) => {
      const text = event.results[0][0].transcript;
      onResult(text);
      setIsListening(false);
    };

    recognition.current.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
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
    try {
      const audioContent = await generateSpeechFromText(text);
      if (audioContent) {
        return new Promise((resolve) => {
          const audio = new Audio('data:audio/mp3;base64,' + audioContent);
          setIsTalking(true);
          audio.onended = () => {
            setIsTalking(false);
            resolve();
          };
          audio.play().catch((e) => {
            console.error('Autoplay prevented:', e);
            setIsTalking(false);
            resolve();
          });
        });
      }
    } catch (error) {
      console.error('Speech synthesis error:', error);
      setIsTalking(false);
    }
  }, []);

  return {
    isListening,
    isTalking,
    startListening,
    speak,
    setIsTalking
  };
};
