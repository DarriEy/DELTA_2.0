// Define the API base URL dynamically. Prefer environment variable if provided;
// otherwise fall back to a default production endpoint. We don't log this
// value to avoid leaking environment details in the browser console.
const API_BASE_URL = import.meta.env?.VITE_APP_API_BASE_URL || 'https://delta-backend-zom0.onrender.com';

/**
 * Request speech synthesis from the backend. Returns a base64 encoded audio
 * string on success or `null` if the request fails. Errors are logged and
 * swallowed so that callers can handle `null` gracefully.
 *
 * @param {string} text The text to convert to speech
 * @returns {Promise<string|null>} The audio content or null
 */
export async function generateSpeechFromText(text) {
  try {
    const response = await fetch(`${API_BASE_URL}/tts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    if (!response.ok) {
      const errorBody = await response.text().catch(() => '');
      console.error('generateSpeechFromText error:', response.status, errorBody);
      return null;
    }
    const data = await response.json();
    return data?.audioContent ?? null;
  } catch (error) {
    console.error('generateSpeechFromText exception:', error);
    return null;
  }
}

/**
 * Request an image from the backend given a prompt. Returns the image URL on
 * success or `null` on failure. All errors are caught and logged. This
 * prevents unhandled exceptions from bubbling into the UI.
 *
 * @param {string} prompt The text describing the desired image
 * @returns {Promise<string|null>} The URL of the generated image or null
 */
export async function generateImageFromPrompt(prompt) {
  try {
    const response = await fetch(`${API_BASE_URL}/generate_image/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt }),
    });
    if (!response.ok) {
      const errorBody = await response.text().catch(() => '');
      console.error('generateImageFromPrompt error:', response.status, errorBody);
      return null;
    }
    const data = await response.json();
    return data?.image_url ?? null;
  } catch (error) {
    console.error('generateImageFromPrompt exception:', error);
    return null;
  }
}
