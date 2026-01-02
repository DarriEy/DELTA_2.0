import { useCallback, useState } from "react";
import { useAvatarAnimations } from "./useAvatarAnimations";

export const useChatInteraction = ({
  sendMessage,
  addLocalAssistantMessage,
}) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [introductionSpoken, setIntroductionSpoken] = useState(false);
  const [isChatActive, setIsChatActive] = useState(false);
  
  const {
    isNodding,
    isShaking,
    triggerShake
  } = useAvatarAnimations(isProcessing);

  const handleAvatarClick = useCallback(async () => {
    console.log("DELTA: Avatar clicked.");

    setIsChatActive(true);

    if (!introductionSpoken) {
      const greeting =
        "Hi I'm Delta, your personal hydrological research assistant. How should we save the world today?";
      console.log("DELTA: Showing introduction...");
      
      if (addLocalAssistantMessage) {
        addLocalAssistantMessage(greeting);
      }
      setIntroductionSpoken(true);
    }
  }, [
    introductionSpoken,
    addLocalAssistantMessage,
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
