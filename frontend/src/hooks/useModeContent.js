import { useCallback, useState } from "react";
import educationalContent from "../educationalContent.json";
import modelingContent from "../modelingContent.json";
import dataAnalysisContent from "../dataAnalysisContent.json";

export const useModeContent = ({
  activeMode,
  setActiveMode,
  backgrounds,
  generateBackground,
}) => {
  const [showContentFrame, setShowContentFrame] = useState(false);
  const [currentEducationalContent, setCurrentEducationalContent] = useState(null);
  const [currentModelingContent, setCurrentModelingContent] = useState(null);
  const [currentDataAnalysisContent, setCurrentDataAnalysisContent] = useState(null);

  const switchMode = useCallback(
    async (mode) => {
      if (activeMode === mode) return;

      setShowContentFrame(false);
      setActiveMode(mode);

      if (mode === "educational") {
        setCurrentEducationalContent(educationalContent.hydrology101);
        if (!backgrounds.educational) {
          const prompt =
            "Please generate a photorealistic image of a university classroom from the perspective of a student...";
          await generateBackground("educational", prompt);
        }
      } else if (mode === "modeling") {
        setCurrentModelingContent(modelingContent.intro);
        if (!backgrounds.modeling) {
          const prompt =
            "Please create a photorealistic image of the interior of an advanced hydrological monitoring space...";
          await generateBackground("modeling", prompt);
        }
      } else if (mode === "dataAnalysis") {
        setCurrentDataAnalysisContent(dataAnalysisContent.intro);
        if (!backgrounds.dataAnalysis) {
          const prompt =
            "Please generate a photorealistic, top-down view of a modern, hydrological data analysis idea board...";
          await generateBackground("dataAnalysis", prompt);
        }
      }

      setShowContentFrame(true);
    },
    [activeMode, setActiveMode, backgrounds, generateBackground]
  );

  return {
    showContentFrame,
    currentEducationalContent,
    currentModelingContent,
    currentDataAnalysisContent,
    switchMode,
  };
};
