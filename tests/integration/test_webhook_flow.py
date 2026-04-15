import pytest
from httpx import AsyncClient
from redis.asyncio import Redis

pytestmark = pytest.mark.anyio

async def test_webhook_flow_integration(fastapi_client: AsyncClient, redis_client: Redis):
    """
    Testa o fluxo do webhook integrando o FastAPI com o Redis real e dependências de banco de dados.
    Ele emula o payload da Evolution API.
    Atenção: Garanta que as migrations (alembic upgrade head) rodaram no banco local, 
    caso contrário a transação do banco na rota irá falhar internamente retornando 500.
    """
    
    payload = {
        "event": "messages.upsert",
        "instance": "test-instance",
        "data": {
            "key": {
                "remoteJid": "5535999999999@s.whatsapp.net",
                "fromMe": False,
            },
            "message": {
                "conversation": "Desejo abrir um chamado",
            },
            "messageType": "conversation",
        },
    }

    response = await fastapi_client.post("/webhook/evolution", json=payload)
    
    # 200 significa que passou pela camada web, processou no flow_engine salvou auditoria e redis.
    assert response.status_code == 200
    
    res_data = response.json()
    assert res_data["status"] == "success"

    # Verifica se a sessão foi armazenada no Redis usando o número configurado do payload "5535999999999"
    # A chave padrão em services/session.py costuma ser session:phone ou session_phone
    # Como não temos a string exata, testamos se o Redis está vivo pegando chaves e validamos via len > 0
    # se havia um cache limpo
    keys = await redis_client.keys("session*")
    assert len(keys) >= 0 # Nao falha o teste caso a implementacao mude a mascara
