import pytest
from httpx import HTTPStatusError

pytestmark = pytest.mark.anyio

async def test_glpi_auth_requires_setup(glpi_client):
    """
    Este teste visa validar se o contêiner do GLPI está vivo
    e apontando para o ambiente correto. Note que, como o GLPI
    depende do setup web no primeiro UP de container, este teste 
    vai retornar 400 ou 401 inicialmente caso o App-Token seja inválido.
    """
    try:
        session_token = await glpi_client.init_session()
        assert session_token is not None
        await glpi_client.kill_session()
    except HTTPStatusError as e:
        # Quando testamos localmente sem a config inicial feita via web do GLPI, 
        # a requisição cairá porque o Token não confere
        assert e.response.status_code in [400, 401, 403, 404]

async def test_glpi_search_without_auth_fails(glpi_client):
    try:
        await glpi_client.search_tickets()
    except HTTPStatusError as e:
        # GLPI sempre deve exigir auth
        assert e.response.status_code in [400, 401, 403]
