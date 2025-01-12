// services.js
export const generateSpeechFromText = async (text) => {
  try {
    const response = await fetch("http://localhost:3001/api/tts", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text }),
    });

    console.log("TTS response status:", response.status);

    if (!response.ok) {
      const errorBody = await response.text();
      console.error("TTS error body:", errorBody);
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data.audioContent;
  } catch (error) {
    console.error("Error during text-to-speech:", error);
    throw error; // Re-throw to be handled by the caller
  }
};

export const generateImageFromPrompt = async (prompt) => {
  try {
    console.log("Sending prompt to backend:", prompt); // Log the prompt
    const response = await fetch(`http://localhost:8000/api/generate_image`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ prompt }), // Make sure 'prompt' is a string
    });

    if (response.ok) {
      const data = await response.json();
      return data.image_url;
    } else {
      const errorData = await response.json();
      console.error("Failed to generate image:", errorData.detail);
      throw new Error("Failed to generate image");
    }
  } catch (error) {
    console.error("Error generating image:", error);
    throw error; // Re-throw to be handled by the caller
  }
};
