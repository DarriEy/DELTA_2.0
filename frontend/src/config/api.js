const DEFAULT_RENDER_URL = "https://delta-backend-zom0.onrender.com";

const normalizeBaseUrl = (url) => {
  if (!url) return "";
  return url.endsWith("/") ? url.slice(0, -1) : url;
};

const appendApiPath = (url) => {
  if (url.endsWith("/api")) return url;
  return `${url}/api`;
};

export const resolveApiBaseUrl = ({
  envUrl,
  hostname,
  defaultRenderUrl = DEFAULT_RENDER_URL,
}) => {
  const baseEnvUrl = normalizeBaseUrl(envUrl);
  const baseDefaultUrl = normalizeBaseUrl(defaultRenderUrl);

  if (hostname === "localhost" || hostname === "127.0.0.1") {
    if (
      !baseEnvUrl ||
      baseEnvUrl.includes("herokuapp.com") ||
      baseEnvUrl.includes("onrender.com")
    ) {
      return "http://localhost:8000/api";
    }
    return appendApiPath(baseEnvUrl);
  }

  if (hostname.includes("github.io")) {
    if (!baseEnvUrl || baseEnvUrl.includes("herokuapp.com")) {
      return appendApiPath(baseDefaultUrl);
    }
  }

  return appendApiPath(baseEnvUrl || baseDefaultUrl);
};

export const getApiBaseUrl = () => {
  const envUrl =
    import.meta.env?.VITE_API_BASE_URL ||
    import.meta.env?.VITE_APP_API_BASE_URL;
  const hostname = window.location.hostname;
  return resolveApiBaseUrl({ envUrl, hostname });
};
