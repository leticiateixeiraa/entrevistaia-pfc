// feat(auth-frontend): cria tela de cadastro/login e armazenamento do token

import api from "./api";

export interface RegisterPayload {
  email: string;
  password: string;
  name?: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export async function register(payload: RegisterPayload) {
  const { data } = await api.post("/auth/register", payload);
  return data;
}

export async function login(payload: LoginPayload) {
  const { data } = await api.post<{ access_token: string; token_type: string }>(
    "/auth/login",
    payload
  );
  localStorage.setItem("access_token", data.access_token);
  return data;
}

export function logout() {
  localStorage.removeItem("access_token");
}

export function isAuthenticated(): boolean {
  return Boolean(localStorage.getItem("access_token"));
}
