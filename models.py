from sqlalchemy import Column, Integer, String, Float, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    prediction = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)