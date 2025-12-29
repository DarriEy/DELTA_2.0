const API_BASE_URL = 'https://delta-backend-zom0.onrender.com' //import.meta.env.VITE_APP_API_BASE_URL;

console.log("API_BASE_URL in services:", API_BASE_URL);

export async function generateSpeechFromText(text) {
  console.log("Text to be spoken:", text);
  const response = await fetch(`${API_BASE_URL}/api/tts`, { // Use API_BASE_URL
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text }),
  });
  console.log("TTS response status:", response.status); // Log the status code

  if (response.ok) {
    const data = await response.json();
    return data.audioContent;
  } else {
    const errorBody = await response.text();
    console.error("Error body:", errorBody);
    throw new Error(`HTTP error! status: ${response.status}`);
  }
}

export const generateImageFromPrompt = async (prompt) => {
  try {
    if (!API_BASE_URL) {
      throw new Error("API_BASE_URL is not defined!");
    }

    console.log("Sending prompt to backend:", prompt);
    const url = `${API_BASE_URL}/api/generate_image/`;
    console.log("Making request to:", url);

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
      const errorData = await response.text(); // Try to get text response
      console.error("Failed to generate image:", errorData);
      throw new Error(
        `Failed to generate image: ${errorData || response.statusText}`
      );
    }
  } catch (error) {
    console.error("Error generating image:", error);
    throw error;
  }
};