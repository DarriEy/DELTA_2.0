import { apiClient } from './api/client';

/**
 * Request speech synthesis from the backend.
 */
export async function generateSpeechFromText(text) {
  try {
    const data = await apiClient.post('/tts', { text });
    return data?.audioContent ?? null;
  } catch (error) {
    console.error('generateSpeechFromText exception:', error);
    return null;
  }
}

/**
 * Request an image from the backend given a prompt.
 */
export async function generateImageFromPrompt(prompt) {
  try {
    const data = await apiClient.post('/generate_image/', { prompt });
    return data?.image_url ?? null;
  } catch (error) {
    console.error('generateImageFromPrompt exception:', error);
    return null;
  }
}
