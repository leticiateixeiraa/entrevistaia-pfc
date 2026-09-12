// feat(auth-frontend): protege rotas que exigem usuário autenticado
//
// Uso:
//   <Route element={<ProtectedRoute />}>
//     <Route path="/welcome" element={<Welcome />} />
//   </Route>
//
// Checagem local e imediata (token existe no localStorage). A validade real
// do token é sempre conferida pelo back-end a cada chamada; se o token
// estiver expirado ou inválido, o endpoint retorna 401 e a página trata isso.

import { Navigate, Outlet } from "react-router-dom";
import { isAuthenticated } from "../services/authService";

export default function ProtectedRoute() {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  return <Outlet />;
}