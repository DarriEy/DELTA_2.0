const getApiBaseUrl = () => {
  const envUrl = import.meta.env?.VITE_APP_API_BASE_URL;
  const hostname = window.location.hostname;
  const RENDER_URL = 'https://delta-backend-zom0.onrender.com';
  
  // 1. Local Development
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    // If we're local but the env says Heroku/Render, use local backend instead
    if (!envUrl || envUrl.includes('herokuapp.com') || envUrl.includes('onrender.com')) {
      return 'http://localhost:8000/api';
    }
    return envUrl + '/api';
  }
  
  // 2. Production (GitHub Pages)
  if (hostname.includes('github.io')) {
    // Prefer Render over Heroku if both are present or env is missing
    if (!envUrl || envUrl.includes('herokuapp.com')) {
      return RENDER_URL + '/api';
    }
  }
  
  return (envUrl || RENDER_URL) + '/api';
};

const API_BASE_URL = getApiBaseUrl();

const handleResponse = async (response) => {
  if (!response.ok) {
    const errorBody = await response.text().catch(() => '');
    throw new Error(`API Error ${response.status}: ${errorBody}`);
  }
  return response.json();
};

export const apiClient = {
  async post(endpoint, data) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  async get(endpoint) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`);
    return handleResponse(response);
  },

  async patch(endpoint, data) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  async put(endpoint, data) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  async stream(endpoint, data, onChunk) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`Stream Error ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let result = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value, { stream: true });
      result += chunk;
      if (onChunk) onChunk(chunk);
    }
    return result;
  }
};
