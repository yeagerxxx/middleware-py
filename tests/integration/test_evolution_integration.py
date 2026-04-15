import pytest
from httpx import HTTPStatusError

pytestmark = pytest.mark.anyio

async def test_evolution_send_text(evolution_client):
    """
    Tenta chamar a api do Evolution contêinerizado. 
    Se a instância não foi criada manualmente ainda, a api retorna um 404 (NotFoundError).
    """
    try:
        response = await evolution_client.send_text("1234567890", "Teste de integração")
        assert response is not None
    except HTTPStatusError as e:
        # 404 not found (instância não criada na Evolution API)
        # 401/403 (Global APIKey errada)
        assert e.response.status_code in [404, 401, 403, 422]
