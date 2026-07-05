from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from .database import Base

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True, index=True)
    rubrics = Column(ARRAY(String))
    text = Column(Text)
    created_date = Column(DateTime)