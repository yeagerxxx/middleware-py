from __future__ import annotations

import httpx


class EvolutionClient:
    """Client HTTP assíncrono para a Evolution API (WhatsApp)."""

    def __init__(self, base_url: str, api_key: str, instance: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.instance = instance
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def send_text(self, number: str, text: str) -> dict:
        """
        Envia uma mensagem de texto simples.
        """
        headers = self._build_headers()
        payload = {"number": number, "text": text}
        response = await self._client.post(
            f"/message/sendText/{self.instance}",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    async def send_buttons(
        self, number: str, title: str, buttons: list[dict]
    ) -> dict:
        """
        Envia mensagem com botões interativos.
        """
        headers = self._build_headers()
        payload = {
            "number": number,
            "title": title,
            "buttons": buttons,
        }
        response = await self._client.post(
            f"/message/sendButtons/{self.instance}",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    async def send_list(
        self, number: str, title: str, description: str, sections: list[dict]
    ) -> dict:
        """
        Envia mensagem com lista de opções.
        """
        headers = self._build_headers()
        payload = {
            "number": number,
            "title": title,
            "description": description,
            "sections": sections,
        }
        response = await self._client.post(
            f"/message/sendList/{self.instance}",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    def _build_headers(self) -> dict[str, str]:
        """Monta headers padrão com apikey."""
        return {
            "Content-Type": "application/json",
            "apikey": self.api_key,
        }

    async def close(self) -> None:
        """Fecha o client HTTP."""
        await self._client.aclose()
