// Instância única de HTTP client, compartilhada por todos os services
// (auth, questions, interview). Anexa o token JWT automaticamente
// quando existir, seguindo o contrato combinado com o time:
//   header Authorization: Bearer <token>

import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
