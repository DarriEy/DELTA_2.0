import { useCallback, useEffect, useRef, useState } from "react";

export const useSpeechInteraction = ({
  sendMessage,
  startListening,
  speak,
  isListening,
  isTalking,
}) => {
  const [isNodding, setIsNodding] = useState(false);
  const [isShaking, setIsShaking] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [introductionSpoken, setIntroductionSpoken] = useState(false);
  const [speechQueue, setSpeechQueue] = useState([]);
  const [isSpeakingChunk, setIsSpeakingChunk] = useState(false);

  const bufferedText = useRef("");
  const speechQueueRef = useRef([]);
  const isSpeakingChunkRef = useRef(false);
  const isListeningRef = useRef(false);
  const sentenceEndings = /[.!?。？！]/;

  useEffect(() => {
    speechQueueRef.current = speechQueue;
  }, [speechQueue]);

  useEffect(() => {
    isSpeakingChunkRef.current = isSpeakingChunk;
  }, [isSpeakingChunk]);

  useEffect(() => {
    isListeningRef.current = isListening;
  }, [isListening]);

  useEffect(() => {
    setIsNodding(isTalking);
  }, [isTalking]);

  const triggerShake = useCallback(() => {
    setIsShaking(true);
    setTimeout(() => setIsShaking(false), 1000);
  }, []);

  useEffect(() => {
    if (speechQueue.length > 0 && !isSpeakingChunk) {
      const nextSentence = speechQueue[0];
      setIsSpeakingChunk(true);
      speak(nextSentence).then(() => {
        setSpeechQueue((prev) => prev.slice(1));
        setIsSpeakingChunk(false);
      });
    }
  }, [speechQueue, isSpeakingChunk, speak]);

  const processTextChunk = useCallback((chunk) => {
    bufferedText.current += chunk;
    let match;
    while ((match = bufferedText.current.match(sentenceEndings))) {
      const sentence = bufferedText.current
        .substring(0, match.index + 1)
        .trim();
      if (sentence) {
        setSpeechQueue((prev) => [...prev, sentence]);
      }
      bufferedText.current = bufferedText.current.substring(match.index + 1);
    }
  }, []);

  const handleSpeechRecognitionResult = useCallback(
    async (text) => {
      if (!text) return;
      setIsProcessing(true);
      bufferedText.current = "";

      try {
        await sendMessage(text, processTextChunk);

        if (bufferedText.current.trim()) {
          setSpeechQueue((prev) => [...prev, bufferedText.current.trim()]);
          bufferedText.current = "";
        }

        const checkAndStartListening = () => {
          if (
            speechQueueRef.current.length === 0 &&
            !isSpeakingChunkRef.current &&
            !isListeningRef.current
          ) {
            console.log("DELTA: Speech queue empty, starting to listen again...");
            startListening(handleSpeechRecognitionResult);
          } else {
            setTimeout(checkAndStartListening, 500);
          }
        };
        checkAndStartListening();
      } catch (error) {
        console.error(error);
        triggerShake();
        setIsProcessing(false);
      } finally {
        setIsProcessing(false);
      }
    },
    [sendMessage, processTextChunk, startListening, triggerShake]
  );

  const handleAvatarClick = useCallback(async () => {
    console.log("DELTA: Avatar clicked. State:", {
      introductionSpoken,
      isListening,
      isTalking,
    });

    if (!introductionSpoken) {
      const greeting =
        "Hi I'm Delta, your personal hydrological research assistant. How should we save the world today?";
      console.log("DELTA: Speaking introduction...");
      try {
        await speak(greeting);
        setIntroductionSpoken(true);
        console.log("DELTA: Greeting finished, starting to listen...");
        startListening(handleSpeechRecognitionResult, (error) => {
          console.error(
            `DELTA: Speech recognition error during initial listen: ${error}`
          );
          triggerShake();
        });
      } catch (err) {
        console.error("DELTA: Speech failed:", err);
      }
    } else if (!isListening && !isTalking) {
      console.log("DELTA: Starting speech recognition...");
      startListening(handleSpeechRecognitionResult, (error) => {
        console.error(`Speech recognition error: ${error}`);
        triggerShake();
      });
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
    setIsProcessing,
    handleAvatarClick,
    triggerShake,
  };
};
