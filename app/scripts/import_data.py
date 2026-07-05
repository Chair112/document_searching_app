import csv
import ast
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal, engine, Base
from app.models import Document
from app.es_client import es_client, init_es

async def wait_for_es():
    """Ждем поднятия Elasticsearch"""
    for _ in range(15):
        try:
            if await es_client.ping():
                return
        except Exception:
            pass
        await asyncio.sleep(2)
    raise Exception("Elasticsearch not available")

async def import_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    await wait_for_es()
    await init_es()
    
    documents = []
    # Убедись, что файл data.csv лежит в корне проекта
    with open('posts.txt', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader) # Пропускаем заголовок
        for row in reader:
            if len(row) < 3:
                continue
            
            text = row[0]
            created_date_str = row[1]
            rubrics_str = row[2]
            
            try:
                created_date = datetime.strptime(created_date_str, '%Y-%m-%d %H:%M:%S')
                rubrics = ast.literal_eval(rubrics_str)
                documents.append({
                    'text': text,
                    'created_date': created_date,
                    'rubrics': rubrics
                })
            except Exception as e:
                print(f"Error parsing row: {e}")
                
    async with AsyncSessionLocal() as session:
        for i, doc_data in enumerate(documents):
            doc_id = i + 1
            doc = Document(id=doc_id, **doc_data)
            session.add(doc)
            
            # Индексируем в Elasticsearch
            await es_client.index(
                index="documents",
                id=doc_id,
                document={
                    "id": doc_id,
                    "text": doc_data['text']
                }
            )
        await session.commit()
    print(f"Successfully imported {len(documents)} documents.")

if __name__ == "__main__":
    asyncio.run(import_data())