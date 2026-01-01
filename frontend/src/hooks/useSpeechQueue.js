import { useState, useRef, useEffect, useCallback } from 'react';

export const useSpeechQueue = (speak) => {
  const [speechQueue, setSpeechQueue] = useState([]);
  const [isSpeakingChunk, setIsSpeakingChunk] = useState(false);
  const bufferedText = useRef("");
  const sentenceEndings = /[.!?。？！]/;

  // Process a text chunk and add complete sentences to the queue
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

  // Flush any remaining text in the buffer to the queue
  const flushBuffer = useCallback(() => {
    if (bufferedText.current.trim()) {
      setSpeechQueue((prev) => [...prev, bufferedText.current.trim()]);
      bufferedText.current = "";
    }
  }, []);

  // Clear the queue and buffer
  const clearQueue = useCallback(() => {
    setSpeechQueue([]);
    bufferedText.current = "";
    setIsSpeakingChunk(false);
  }, []);

  // Effect to process the speech queue
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

  return {
    speechQueue,
    isSpeakingChunk,
    processTextChunk,
    flushBuffer,
    clearQueue,
    bufferedText: bufferedText.current
  };
};
