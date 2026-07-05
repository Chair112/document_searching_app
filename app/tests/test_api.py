import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_search_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/search?q=привет")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Проверяем структуру ответа, если данные есть
        if data:
            assert "id" in data[0]
            assert "text" in data[0]

@pytest.mark.asyncio
async def test_delete_endpoint_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete("/documents/999999")
        assert response.status_code == 404