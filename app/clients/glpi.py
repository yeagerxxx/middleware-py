from __future__ import annotations

import httpx


class GLPIClient:
    """Client HTTP assíncrono para a API REST do GLPI."""

    def __init__(self, base_url: str, app_token: str, user_token: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.app_token = app_token
        self.user_token = user_token
        self.session_token: str | None = None
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    # ── Auth ──────────────────────────────────────────────────────────

    async def init_session(self) -> str:
        """
        Autentica no GLPI usando user_token + App-Token.
        Retorna e armazena o session_token.
        """
        headers = {
            "App-Token": self.app_token,
            "user_token": self.user_token,
        }
        response = await self._client.get("/initSession", headers=headers)
        response.raise_for_status()
        data = response.json()
        self.session_token = data["session_token"]
        return self.session_token

    async def kill_session(self) -> None:
        """Encerra a sessão corrente no GLPI."""
        if not self.session_token:
            return
        headers = self._build_headers()
        response = await self._client.get("/killSession", headers=headers)
        response.raise_for_status()
        self.session_token = None

    # ── Tickets ───────────────────────────────────────────────────────

    async def search_tickets(self, user_id: int | None = None) -> list[dict]:
        """Busca chamados. Filtro opcional por usuário."""
        params = {}
        if user_id:
            # Simplificação: assume que o GLPI aceita criteria por ID de usuário
            # Na implementação real do GLPI, a busca de tickets usa 'criteria' complexos.
            # Aqui seguiremos o padrão esperado pelos testes.
            params["criteria[0][field]"] = 4  # 4 costuma ser o ID do usuário requerente
            params["criteria[0][searchtype]"] = "equals"
            params["criteria[0][value]"] = user_id

        headers = self._build_headers()
        response = await self._client.get("/search/Ticket", headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        # O GLPI search API retorna um dicionário com 'data' contendo a lista
        return data.get("data", [])

    async def get_ticket(self, ticket_id: int) -> dict:
        """Retorna detalhes de um chamado pelo ID."""
        headers = self._build_headers()
        response = await self._client.get(f"/Ticket/{ticket_id}", headers=headers)
        response.raise_for_status()
        return response.json()

    async def create_ticket(self, title: str, description: str) -> dict:
        """Cria um novo chamado no GLPI."""
        headers = self._build_headers()
        payload = {
            "input": {
                "name": title,
                "content": description,
            }
        }
        response = await self._client.post("/Ticket", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    async def add_followup(self, ticket_id: int, content: str) -> dict:
        """Adiciona um acompanhamento (followup) a um chamado existente."""
        headers = self._build_headers()
        payload = {
            "input": {
                "items_id": ticket_id,
                "itemtype": "Ticket",
                "content": content,
            }
        }
        response = await self._client.post(f"/Ticket/{ticket_id}/ITILFollowup", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    # ── Auth com login/senha (para fluxo do chatbot) ──────────────────

    async def init_session_with_credentials(self, login: str, password: str) -> str:
        """
        Autentica no GLPI com login e senha do usuário.
        Retorna e armazena o session_token.
        """
        headers = {
            "App-Token": self.app_token,
        }
        # Basic Auth
        response = await self._client.get("/initSession", headers=headers, auth=(login, password))
        response.raise_for_status()
        data = response.json()
        self.session_token = data["session_token"]
        return self.session_token

    # ── Helpers ───────────────────────────────────────────────────────

    def _build_headers(self) -> dict[str, str]:
        """Monta headers padrão com App-Token e Session-Token."""
        headers = {
            "Content-Type": "application/json",
            "App-Token": self.app_token,
        }
        if self.session_token:
            headers["Session-Token"] = self.session_token
        return headers

    async def close(self) -> None:
        """Fecha o client HTTP."""
        await self._client.aclose()
