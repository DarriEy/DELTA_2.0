const API_BASE_URL = import.meta.env.VITE_APP_API_BASE_URL || 'http://localhost:8000';

console.log('API_BASE_URL in services:', API_BASE_URL); // Add this for debugging

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
    console.log("Sending prompt to backend:", prompt);
    // Remove any trailing slashes from the base URL
    const baseUrl = API_BASE_URL.replace(/\/+$/, '');
    const url = `${baseUrl}/api/generate_image/`;
    console.log("Making request to:", url); // Add this for debugging
    
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ prompt }),
    });

    if (response.ok) {
      const data = await response.json();
      return data.image_url;
    } else {
      const errorData = await response.json();
      console.error("Failed to generate image:", errorData.detail);
      throw new Error(`Failed to generate image: ${errorData.detail}`);
    }
  } catch (error) {
    console.error("Error generating image:", error);
    throw error;
  }
};