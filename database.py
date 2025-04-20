import datetime
from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from flask import request, jsonify

DB_URL = "sqlite:///predictions.db"
Base = declarative_base()
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

class Prediction(Base):
    __tablename__ = 'predictions'
    id = Column(Integer, primary_key=True)
    sepal_length = Column(Float, nullable=False)
    sepal_width = Column(Float, nullable=False)
    petal_length = Column(Float, nullable=False)
    petal_width = Column(Float, nullable=False)
    predicted_class = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(engine)

def save_prediction(**kwargs):
    session = Session()
    pred = Prediction(**kwargs)
    session.add(pred)
    session.commit()
    session.close()

def list_predictions():
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    session = Session()
    preds = session.query(Prediction).offset(offset).limit(limit).all()
    session.close()
    return jsonify([
        {
            "id": p.id,
            "sepal_length": p.sepal_length,
            "sepal_width": p.sepal_width,
            "petal_length": p.petal_length,
            "petal_width": p.petal_width,
            "predicted_class": p.predicted_class,
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M:%S")
        } for p in preds
    ])
