import os
import logging
import datetime
import jwt
from functools import wraps
from flask import Flask, request, jsonify
import joblib
import numpy as np
from sqlalchemy import Float, create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

JWT_SECRET = "MEUSEGREDOAQUI"
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600  # 1 hour

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_modelo")

DB_URL = "sqlite:///predictions.db"
engine = create_engine(DB_URL, echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)

# Define the Prediction model
class Prediction(Base):
    __tablename__ = 'predictions'
    id = Column(Integer, primary_key=True, autoincrement=True)  
    sepal_length = Column(Float, nullable=False)
    sepal_width = Column(Float, nullable=False)
    petal_length = Column(Float, nullable=False)
    petal_width = Column(Float, nullable=False)
    predicted_class = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Create the table if it doesn't exist
Base.metadata.create_all(engine)

model = joblib.load("iris_model.pkl")
logger.info("Modelo carregado com sucesso.")

app = Flask(__name__)
predictions_cache = {}

TEST_USERNAME = "admin"
TEST_PASSWORD = "secret"

def create_jwt_token(username):
    payload = {
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }   
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"message": "Token is missing!"}), 401
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            logger.info(f"Token validado para o usuário: {payload['username']}")
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True)
    username = data.get('username')
    password = data.get('password')
    if username == TEST_USERNAME and password == TEST_PASSWORD:
        token = create_jwt_token(username)
        return jsonify({"token": token}), 200
    else:
        return jsonify({"message": "Invalid credentials!"}), 401
    
@app.route('/predict', methods=['POST'])
@token_required
def predict():
    """
        Endpoint to make predictions using the trained model.
        Corpo (JSON):
        {
            "sepal_length": float,
            "sepal_width": float,
            "petal_length": float,
            "petal_width": float
        }
        
    """

    data = request.get_json(force=True)
    try:
        sepal_length = float(data['sepal_length'])
        sepal_width = float(data['sepal_width'])
        petal_length = float(data['petal_length'])
        petal_width = float(data['petal_width'])
    except (ValueError, TypeError) as e:
        logger.error(f"Erro ao processar os dados de entrada: {e}")
        return jsonify({"message": "Invalid input data!"}), 400

    #verifica se já está no cache
    features = (sepal_length, sepal_width, petal_length, petal_width)
    if features in predictions_cache:
        logger.info("Cache hit para %s", features)
        prediction_class = predictions_cache[features]
    else:
        #Rodar o modelo
        input_data = np.array([features])
        prediction = model.predict(input_data)
        prediction_class = int(prediction[0])
        #armazena no cache
        predictions_cache[features] = prediction_class
        logger.info("Predição realizada para %s: %d", features, prediction_class)

        
    prediction = model.predict(features)[0]

    # Save prediction to database
    session = Session()
    new_prediction = Prediction(
        sepal_length=sepal_length,
        sepal_width=sepal_width,
        petal_length=petal_length,
        petal_width=petal_width,
        predicted_class=int(prediction)
    )
    session.add(new_prediction)
    session.commit()
    session.close()

    return jsonify({"predicted_class": int(prediction)}), 200

@app.route('/predictions', methods=['GET'])
@token_required
def list_predictions():
    """
        Endpoint to list all predictions made by the model.
    """
    limit = request.args.get('limit', default=10, type=int)
    offset = request.args.get('offset', default=0, type=int)
    db = Session()
    predictions = db.query(Prediction).offset(offset).limit(limit).all()
    db.close()
    results = []
    for prediction in predictions:
        results.append({
            "id": prediction.id,
            "sepal_length": prediction.sepal_length,
            "sepal_width": prediction.sepal_width,
            "petal_length": prediction.petal_length,
            "petal_width": prediction.petal_width,
            "predicted_class": prediction.predicted_class,
            "created_at": prediction.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    return jsonify(results), 200
