from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from elasticsearch import NotFoundError

from .database import get_db, engine, Base
from .models import Document
from .schemas import DocumentResponse
from .es_client import es_client, init_es

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await init_es()
    yield
    # Shutdown
    await es_client.close()

app = FastAPI(
    title="Document Search Service",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/search", response_model=List[DocumentResponse])
async def search_documents(q: str = Query(..., min_length=1), db: AsyncSession = Depends(get_db)):
    # 1. Ищем в Elasticsearch (получаем до 1000 релевантных ID)
    try:
        res = await es_client.search(
            index="documents",
            query={"match": {"text": q}},
            size=1000
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Elasticsearch error: {str(e)}")
        
    ids = [hit["_source"]["id"] for hit in res["hits"]["hits"]]
    
    if not ids:
        return []
        
    # 2. Достаем из БД, сортируем по дате и берем первые 20
    stmt = select(Document).where(Document.id.in_(ids)).order_by(Document.created_date.desc()).limit(20)
    result = await db.execute(stmt)
    docs = result.scalars().all()
    
    return docs

@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: int, db: AsyncSession = Depends(get_db)):
    # 1. Удаляем из БД
    stmt = select(Document).where(Document.id == doc_id)
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    await db.delete(doc)
    await db.commit()
    
    # 2. Удаляем из индекса Elasticsearch
    try:
        await es_client.delete(index="documents", id=doc_id)
    except NotFoundError:
        pass # Если в индексе уже не было, не страшно
        
    return {"status": "ok", "message": f"Document {doc_id} deleted"}