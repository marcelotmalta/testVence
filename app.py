from flask import Flask
from flasgger import Swagger
from auth import token_required, login_route
from model import predict_route
from database import list_predictions
from monitor import healthcheck

app = Flask(__name__)
swagger = Swagger(app)  # Inicializa Swagger

# Rotas com suas respectivas funções
app.add_url_rule('/login', view_func=login_route, methods=['POST'])
app.add_url_rule('/predict', view_func=token_required(predict_route), methods=['POST'])
app.add_url_rule('/predictions', view_func=token_required(list_predictions), methods=['GET'])
app.add_url_rule('/healthcheck', view_func=healthcheck, methods=['GET'])

if __name__ == '__main__':
    app.run(debug=True)