import os
from elasticsearch import AsyncElasticsearch

ES_URL = os.getenv("ES_URL", "http://localhost:9200")
es_client = AsyncElasticsearch(hosts=[ES_URL])

async def init_es():
    # Создаем индекс, если его нет. Используем русский анализатор для лучшего поиска
    if not await es_client.indices.exists(index="documents"):
        await es_client.indices.create(
            index="documents",
            mappings={
                "properties": {
                    "id": {"type": "integer"},
                    "text": {"type": "text", "analyzer": "russian"}
                }
            }
        )