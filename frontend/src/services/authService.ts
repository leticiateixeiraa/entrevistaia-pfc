// feat(auth-frontend): cria tela de cadastro/login e armazenamento do token

import api from "./api";

// feat(lgpd): versão vigente do Termo de Uso / Política de Privacidade,
// deve acompanhar a constante equivalente no backend (auth/schemas.py).
export const CURRENT_TERMS_VERSION = "1.0";

export interface RegisterPayload {
  email: string;
  password: string;
  name?: string;
  terms_accepted: boolean;
  terms_version?: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface CurrentUser {
  id: string;
  email: string;
  name: string | null;
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

// feat(auth-frontend): busca os dados do usuário autenticado (GET /auth/me)
export async function getCurrentUser(): Promise<CurrentUser> {
  const { data } = await api.get<CurrentUser>("/auth/me");
  return data;
}