// feat(auth-frontend): cria tela de boas-vindas pós-login/cadastro
//
// Fecha visualmente o ciclo ponta-a-ponta da feature 1 (cadastro, login e
// autenticação): busca o usuário autenticado em GET /auth/me e oferece logout.
// Ainda não há nada das features 2 e 3 (Leonardo/Gabriel) integrado aqui.

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getCurrentUser, logout, type CurrentUser } from "../services/authService";

export default function Welcome() {
  const navigate = useNavigate();
  const [user, setUser] = useState<CurrentUser | null>(null);

  useEffect(() => {
    let active = true;

    getCurrentUser()
      .then((data) => {
        if (active) setUser(data);
      })
      .catch(() => {
        // Token ausente, expirado ou inválido: volta pro login.
        logout();
        navigate("/login", { replace: true });
      });

    return () => {
      active = false;
    };
  }, [navigate]);

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  if (!user) {
    return <p className="text-text-400 text-sm">Carregando...</p>;
  }

  const displayName = user.name?.trim() || user.email;

  return (
    <div className="text-left">
      <h2 className="font-display text-2xl font-semibold mb-2">
        Seja bem-vindo(a), {displayName}
      </h2>
      <p className="text-text-400 text-sm mb-8 leading-relaxed">
        Sua conta foi criada e autenticada com sucesso. As próximas etapas —
        escolher uma vaga ou tipo de apresentação e começar sua entrevista
        simulada — chegam nas próximas entregas.
      </p>

      <div className="bg-ink-800 border border-ink-700 rounded px-4 py-3 mb-8">
        <p className="text-sm text-text-100">Conectado(a) como {user.email}</p>
      </div>

      <button
        type="button"
        onClick={handleLogout}
        className="w-full bg-ink-800 border border-ink-700 text-text-100 rounded py-3 font-semibold text-sm cursor-pointer hover:bg-ink-700"
      >
        Sair
      </button>
    </div>
  );
}