import json

def test_login_success(client):
    response = client.post("/login", json={"username": "admin", "password": "secret"})
    assert response.status_code == 200
    assert response.data.decode().startswith("eyJ")  # início típico de JWT

def test_login_failure(client):
    response = client.post("/login", json={"username": "admin", "password": "wrong"})
    assert response.status_code == 401

def test_predict_unauthorized(client):
    response = client.post("/predict", json={
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    })
    assert response.status_code == 401

def test_predict_authorized(client):
    login_resp = client.post("/login", json={"username": "admin", "password": "secret"})
    token = login_resp.data.decode()

    response = client.post("/predict",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2
        }
    )
    assert response.status_code == 200
    assert "predicted_class" in response.json

def test_predictions_list(client):
    login_resp = client.post("/login", json={"username": "admin", "password": "secret"})
    token = login_resp.data.decode()

    response = client.get("/predictions", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json, list)
