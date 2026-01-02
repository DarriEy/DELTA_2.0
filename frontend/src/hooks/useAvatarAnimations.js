import { useState, useCallback, useEffect } from 'react';

export const useAvatarAnimations = (isProcessing) => {
  const [isNodding, setIsNodding] = useState(false);
  const [isShaking, setIsShaking] = useState(false);

  useEffect(() => {
    setIsNodding(isProcessing);
  }, [isProcessing]);

  const triggerShake = useCallback(() => {
    setIsShaking(true);
    setTimeout(() => setIsShaking(false), 1000);
  }, []);

  return {
    isNodding,
    isShaking,
    triggerShake
  };
};
