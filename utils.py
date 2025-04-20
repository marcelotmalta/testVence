predictions_cache = {}

def cache_prediction(model, features):
    if features in predictions_cache:
        return predictions_cache[features]
    prediction = model.predict([features])[0]
    predictions_cache[features] = int(prediction)
    return int(prediction)
