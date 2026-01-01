import { getApiBaseUrl } from "../config/api";

const API_BASE_URL = getApiBaseUrl();

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: any;
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  // API_BASE_URL already ends with /api
  const response = await fetch(`${API_BASE_URL}/users/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData,
  });

  if (!response.ok) {
    let detail = 'Login failed';
    try {
      const errorData = await response.json();
      detail = errorData.detail || detail;
    } catch (e) {}
    throw new Error(detail);
  }

  const data = await response.json();
  localStorage.setItem('token', data.access_token);
  localStorage.setItem('user', JSON.stringify(data.user));
  return data;
}

export function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
}

export function isAuthenticated(): boolean {
  return !!localStorage.getItem('token');
}
