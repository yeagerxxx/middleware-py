from __future__ import annotations

import json

from redis.asyncio import Redis


class SessionManager:
    """Gerenciamento de sessão de conversa usando Redis."""

    KEY_PREFIX = "session:"

    def __init__(self, redis: Redis, ttl_seconds: int = 1800) -> None:
        self._redis = redis
        self._ttl = ttl_seconds

    async def get(self, phone: str) -> dict | None:
        """Busca sessão pelo número de telefone. Retorna None se não existir."""
        data = await self._redis.get(self._key(phone))
        if not data:
            return None
        return json.loads(data)

    async def set(self, phone: str, data: dict) -> None:
        """Salva ou atualiza sessão com TTL."""
        await self._redis.set(
            self._key(phone),
            json.dumps(data),
            ex=self._ttl,
        )

    async def delete(self, phone: str) -> None:
        """Remove sessão."""
        await self._redis.delete(self._key(phone))

    async def update_step(self, phone: str, step: str) -> None:
        """Atualiza apenas o campo 'step' da sessão existente."""
        data = await self.get(phone)
        if data is None:
            # Se não existe, cria uma nova apenas com o step
            data = {"step": step}
        else:
            data["step"] = step

        await self.set(phone, data)

    def _key(self, phone: str) -> str:
        """Gera a chave Redis para o telefone."""
        return f"{self.KEY_PREFIX}{phone}"
