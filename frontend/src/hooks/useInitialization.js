import { useEffect, useRef } from "react";

export const useInitialization = ({
  currentConversationId,
  createNewConversation,
  generateBackground,
}) => {
  const hasInitialized = useRef(false);

  useEffect(() => {
    if (hasInitialized.current) return;
    hasInitialized.current = true;

    const init = async () => {
      console.log("DELTA: Initializing core systems...");
      try {
        let convId = currentConversationId;
        if (!convId) {
          console.log("DELTA: Creating new secure conversation...");
          convId = await createNewConversation("general");
        }

        if (convId) {
          const imagePrompt =
            "Please, render a highly detailed photorealistic, 4K image of a natural landscape showcasing a beautiful hydrological landscape feature. The setting should be a breathtaking natural environment. Emphasize realistic lighting, textures, and reflections in the water. Style should render with sharp focus and intricate details. Use a 16:9 aspect ratio.";
          console.log("DELTA: Generating environmental background...");
          generateBackground("general", imagePrompt);
        }
      } catch (err) {
        console.error("DELTA: Initialization failure:", err);
      }
    };

    init();
  }, [currentConversationId, createNewConversation, generateBackground]);
};
