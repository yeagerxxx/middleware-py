import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import get_settings
from app.clients.glpi import GLPIClient
from app.clients.evolution import EvolutionClient
from redis.asyncio import Redis

settings = get_settings()

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest_asyncio.fixture(scope="session")
async def fastapi_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture(scope="session")
async def glpi_client():
    client = GLPIClient(
        base_url=settings.GLPI_URL,
        app_token=settings.GLPI_APP_TOKEN,
        user_token=settings.GLPI_USER_TOKEN
    )
    yield client
    await client.close()

@pytest_asyncio.fixture(scope="session")
async def evolution_client():
    client = EvolutionClient(
        base_url=settings.EVOLUTION_URL,
        api_key=settings.EVOLUTION_API_KEY,
        instance=settings.EVOLUTION_INSTANCE
    )
    yield client
    await client.close()

@pytest_asyncio.fixture(scope="session")
async def redis_client():
    redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    yield redis
    await redis.aclose()
