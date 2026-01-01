import { getApiBaseUrl } from "../config/api";

const API_BASE_URL = getApiBaseUrl();

class ApiError extends Error {
  constructor(status, data) {
    const message = data?.message || data?.detail || `API Error ${status}`;
    super(message);
    this.status = status;
    this.data = data;
    this.errorCode = data?.error_code;
    this.name = 'ApiError';
  }
}

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const handleResponse = async (response) => {
  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch (e) {
      const text = await response.text().catch(() => '');
      errorData = { message: text };
    }
    throw new ApiError(response.status, errorData);
  }
  
  const json = await response.json();
  // Return the 'data' field if it exists, otherwise return the whole json
  return json.data !== undefined ? json.data : json;
};

const fetchWithRetry = async (url, options, retries = 2, backoff = 500) => {
  try {
    const response = await fetch(url, options);
    if (!response.ok && (response.status === 429 || response.status >= 500) && retries > 0) {
      console.warn(`Retrying request to ${url}. Status: ${response.status}. Retries left: ${retries}`);
      await sleep(backoff);
      return fetchWithRetry(url, options, retries - 1, backoff * 2);
    }
    return response;
  } catch (error) {
    if (retries > 0) {
      console.warn(`Retrying request to ${url} due to network error. Retries left: ${retries}`);
      await sleep(backoff);
      return fetchWithRetry(url, options, retries - 1, backoff * 2);
    }
    throw error;
  }
};

export const apiClient = {
  async post(endpoint, data) {
    const response = await fetchWithRetry(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  async get(endpoint) {
    const response = await fetchWithRetry(`${API_BASE_URL}${endpoint}`);
    return handleResponse(response);
  },

  async patch(endpoint, data) {
    const response = await fetchWithRetry(`${API_BASE_URL}${endpoint}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  async put(endpoint, data) {
    const response = await fetchWithRetry(`${API_BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  async stream(endpoint, data, onChunk) {
    // Retrying streams is more complex as we shouldn't retry after we started receiving data.
    // For simplicity, we only retry the initial connection.
    const response = await fetchWithRetry(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch (e) {
        errorData = { message: `Stream Error ${response.status}` };
      }
      throw new ApiError(response.status, errorData);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let result = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value, { stream: true });
      
      // Parse SSE data
      const lines = chunk.split('\n');
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const content = line.slice(6);
          result += content;
          if (onChunk) onChunk(content);
        }
      }
    }
    return result;
  }
};