import { useMemo } from 'react';

export const useBackgroundStyle = (activeMode, backgrounds) => {
  return useMemo(() => {
    const currentBackground = (() => {
      switch (activeMode) {
        case "educational":
          return backgrounds.educational || backgrounds.general;
        case "modeling":
          return backgrounds.modeling || backgrounds.general;
        case "dataAnalysis":
          return backgrounds.dataAnalysis || backgrounds.general;
        default:
          return backgrounds.general;
      }
    })();

    if (
      currentBackground?.startsWith("data:") ||
      currentBackground?.startsWith("http")
    ) {
      return {
        background: `radial-gradient(circle at center, rgba(15,23,42,0.4) 0%, rgba(2,6,23,1) 100%), url(${currentBackground}) center/cover no-repeat`,
      };
    }

    return {
      background:
        currentBackground || "linear-gradient(135deg, #020617 0%, #0f172a 100%)",
    };
  }, [activeMode, backgrounds]);
};
