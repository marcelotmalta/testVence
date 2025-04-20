import datetime, jwt
from flask import request, jsonify
from functools import wraps

JWT_SECRET = "MEUSEGREDOAQUI"
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600
TEST_USERNAME = "admin"
TEST_PASSWORD = "secret"

def create_jwt_token(username):
    payload = {
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token and token.startswith("Bearer "):
            token = token.split(" ")[1]
        else:
            return jsonify({"message": "Token is missing or malformed!"}), 401

        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 401
        return f(*args, **kwargs)
    return decorated

def login_route():
    """
    Realiza a autenticação do usuário e retorna um token JWT puro.
    ---
    tags:
      - Autenticação
    consumes:
      - application/json
    parameters:
      - in: body
        name: credentials
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: admin
            password:
              type: string
              example: secret
    responses:
      200:
        description: Token JWT gerado
        content:
          text/plain:
            schema:
              type: string
      401:
        description: Credenciais inválidas
    """
    data = request.get_json(force=True)
    username = data.get('username')
    password = data.get('password')
    if username == TEST_USERNAME and password == TEST_PASSWORD:
        token = create_jwt_token(username)
        return token, 200, {'Content-Type': 'text/plain'}
    else:
        return jsonify({"message": "Invalid credentials!"}), 401
