import { useCallback, useEffect, useRef, useState } from "react";
import { useSpeechQueue } from "./useSpeechQueue";
import { useAvatarAnimations } from "./useAvatarAnimations";

export const useSpeechInteraction = ({
  sendMessage,
  addLocalAssistantMessage,
  startListening,
  speak,
  isListening,
  isTalking,
}) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [introductionSpoken, setIntroductionSpoken] = useState(false);
  const [isChatActive, setIsChatActive] = useState(false);
  
  const {
    speechQueue,
    isSpeakingChunk,
    processTextChunk,
    flushBuffer,
    clearQueue
  } = useSpeechQueue(speak);

  const {
    isNodding,
    isShaking,
    triggerShake
  } = useAvatarAnimations(isTalking);

  // Refs for async callbacks
  const isListeningRef = useRef(false);
  const shouldRestartListening = useRef(false);

  useEffect(() => {
    isListeningRef.current = isListening;
  }, [isListening]);

  const isBusy = speechQueue.length > 0 || isSpeakingChunk;

  const handleSpeechRecognitionResult = useCallback(
    async (text) => {
      if (!text) return;
      setIsProcessing(true);
      clearQueue();

      try {
        await sendMessage(text, processTextChunk);
        flushBuffer();
        
        // Signal that we want to restart listening once speech finishes
        shouldRestartListening.current = true;
      } catch (error) {
        console.error(error);
        triggerShake();
        setIsProcessing(false);
      } finally {
        setIsProcessing(false);
      }
    },
    [sendMessage, processTextChunk, triggerShake, flushBuffer, clearQueue]
  );

  useEffect(() => {
    if (!isBusy && shouldRestartListening.current && !isListeningRef.current) {
      console.log("DELTA: Speech queue empty, starting to listen again...");
      startListening(handleSpeechRecognitionResult);
      shouldRestartListening.current = false;
    }
  }, [isBusy, startListening, handleSpeechRecognitionResult]);

  const handleAvatarClick = useCallback(async () => {
    console.log("DELTA: Avatar clicked. State:", {
      introductionSpoken,
      isListening,
      isTalking,
    });

    setIsChatActive(true);

    if (!introductionSpoken) {
      const greeting =
        "Hi I'm Delta, your personal hydrological research assistant. How should we save the world today?";
      console.log("DELTA: Speaking introduction...");
      try {
        // Add to UI history so user sees it
        if (addLocalAssistantMessage) {
          addLocalAssistantMessage(greeting);
        }
        await speak(greeting);
        setIntroductionSpoken(true);
        console.log("DELTA: Greeting finished, attempting to start microphone...");
        startListening(handleSpeechRecognitionResult, (error) => {
          console.error(
            `DELTA: Speech recognition error during initial listen: ${error}`
          );
          triggerShake();
        });
      } catch (err) {
        console.error("DELTA: Initialization sequence failed:", err);
      }
    } else if (!isListening && !isTalking) {
      console.log("DELTA: Manual microphone trigger...");
      startListening(handleSpeechRecognitionResult, (error) => {
        console.error(`Speech recognition error: ${error}`);
        triggerShake();
      });
    } else {
      console.log("DELTA: Cannot start microphone - busy. State:", { isListening, isTalking });
    }
  }, [
    introductionSpoken,
    isListening,
    isTalking,
    speak,
    startListening,
    handleSpeechRecognitionResult,
    triggerShake,
  ]);

  return {
    isNodding,
    isShaking,
    isProcessing,
    isChatActive,
    setIsProcessing,
    handleAvatarClick,
    triggerShake,
  };
};