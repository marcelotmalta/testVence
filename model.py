import joblib
import numpy as np
from flask import request, jsonify
from database import save_prediction
from utils import cache_prediction

model = joblib.load("iris_model.pkl")

def predict_route():
    try:
        data = request.get_json(force=True)
        features = tuple(map(float, (
            data["sepal_length"],
            data["sepal_width"],
            data["petal_length"],
            data["petal_width"]
        )))
    except Exception:
        return jsonify({"message": "Invalid input data!"}), 400

    prediction_class = cache_prediction(model, features)
    save_prediction(
        sepal_length=features[0],
        sepal_width=features[1],
        petal_length=features[2],
        petal_width=features[3],
        predicted_class=prediction_class
    )
    return jsonify({"predicted_class": prediction_class})
