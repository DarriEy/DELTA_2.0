import { resolveApiBaseUrl } from "../api";

test("uses localhost backend for local dev without env override", () => {
  const result = resolveApiBaseUrl({
    envUrl: "",
    hostname: "localhost",
  });

  expect(result).toBe("http://localhost:8000/api");
});

test("uses render backend for github pages without env url", () => {
  const result = resolveApiBaseUrl({
    envUrl: "",
    hostname: "darriey.github.io",
  });

  expect(result).toBe("https://delta-backend-zom0.onrender.com/api");
});

test("uses env url for non-local host", () => {
  const result = resolveApiBaseUrl({
    envUrl: "https://custom.example.com",
    hostname: "delta.example.com",
  });

  expect(result).toBe("https://custom.example.com/api");
});
