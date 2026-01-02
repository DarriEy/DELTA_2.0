import { getApiBaseUrl } from "../config/api";

const API_BASE_URL = getApiBaseUrl();

interface ApiErrorData {
  message?: string;
  detail?: string;
  error_code?: string;
  [key: string]: any;
}

class ApiError extends Error {
  status: number;
  data: ApiErrorData;
  errorCode?: string;

  constructor(status: number, data: ApiErrorData) {
    const message = data?.message || data?.detail || `API Error ${status}`;
    super(message);
    this.status = status;
    this.data = data;
    this.errorCode = data?.error_code;
    this.name = 'ApiError';
  }
}

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

const handleResponse = async (response: Response) => {
  if (!response.ok) {
    let errorData: ApiErrorData;
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

const fetchWithRetry = async (url: string, options?: RequestInit, retries = 2, backoff = 500): Promise<Response> => {
  const token = localStorage.getItem('token');
  const authOptions = { ...options };
  if (token) {
    authOptions.headers = {
      ...authOptions.headers,
      'Authorization': `Bearer ${token}`
    };
  }

  try {
    const response = await fetch(url, authOptions);
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
  async post<T = any>(endpoint: string, data: any): Promise<T> {
    const response = await fetchWithRetry(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  async get<T = any>(endpoint: string): Promise<T> {
    const response = await fetchWithRetry(`${API_BASE_URL}${endpoint}`);
    return handleResponse(response);
  },

  async patch<T = any>(endpoint: string, data: any): Promise<T> {
    const response = await fetchWithRetry(`${API_BASE_URL}${endpoint}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  async put<T = any>(endpoint: string, data: any): Promise<T> {
    const response = await fetchWithRetry(`${API_BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  async stream(endpoint: string, data: any, onChunk?: (chunk: string) => void): Promise<string> {
    const response = await fetchWithRetry(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      let errorData: ApiErrorData;
      try {
        errorData = await response.json();
      } catch (e) {
        errorData = { message: `Stream Error ${response.status}` };
      }
      throw new ApiError(response.status, errorData);
    }

    if (!response.body) {
      throw new Error('Response body is null');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let result = '';
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split('\n\n');
      buffer = parts.pop() || '';

      for (const part of parts) {
        const lines = part.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const raw = line.slice(6);
            try {
              const content = JSON.parse(raw);
              result += content;
              if (onChunk) onChunk(content);
            } catch (e) {
              // Fallback for non-JSON content
              result += raw;
              if (onChunk) onChunk(raw);
            }
          }
        }
      }
    }
    
    // Process remaining buffer
    if (buffer.startsWith('data: ')) {
      const content = buffer.slice(6);
      result += content;
      if (onChunk) onChunk(content);
    }
    
    return result;
  }
};
