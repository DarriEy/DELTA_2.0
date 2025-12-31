import { useState, useCallback } from 'react';
import { generateImageFromPrompt } from '../services';

export const useBackgrounds = () => {
  const [backgrounds, setBackgrounds] = useState({
    general: null,
    educational: null,
    modeling: null,
    dataAnalysis: null
  });
  const [isLoading, setIsLoading] = useState(false);

  const generateBackground = useCallback(async (type, prompt) => {
    setIsLoading(true);
    try {
      const imageUrl = await generateImageFromPrompt(prompt);
      if (imageUrl) {
        setBackgrounds(prev => ({ ...prev, [type]: imageUrl }));
        return imageUrl;
      } else {
        const fallback = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
        setBackgrounds(prev => ({ ...prev, [type]: fallback }));
        return fallback;
      }
    } catch (error) {
      console.error(`Error generating ${type} background:`, error);
      const fallback = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
      setBackgrounds(prev => ({ ...prev, [type]: fallback }));
      return fallback;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    backgrounds,
    isLoading,
    generateBackground
  };
};
