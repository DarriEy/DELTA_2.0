import { apiClient } from './client';

/**
 * Request an image from the backend given a prompt.
 * @param {string} prompt - The image generation prompt.
 * @returns {Promise<string|null>} The image URL/data URI or null on failure.
 */
export async function generateImageFromPrompt(prompt: string): Promise<string | null> {
  try {
    const data = await apiClient.post<{ image_url: string }>('/generate_image/', { prompt });
    return data?.image_url ?? null;
  } catch (error) {
    console.error('generateImageFromPrompt exception:', error);
    throw error;
  }
}