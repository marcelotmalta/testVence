import sys
import os

# Adiciona a raiz do projeto ao path para que os imports funcionem
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from flask import Flask
from flasgger import Swagger
from auth import token_required, login_route
from model import predict_route
from database import list_predictions
from monitor import healthcheck

app = Flask(__name__)
swagger = Swagger(app)

app.add_url_rule('/login', view_func=login_route, methods=['POST'])
app.add_url_rule('/predict', view_func=token_required(predict_route), methods=['POST'])
app.add_url_rule('/predictions', view_func=token_required(list_predictions), methods=['GET'])
app.add_url_rule('/healthcheck', view_func=healthcheck, methods=['GET'])

# Adaptando para Vercel: exportando a app
# Vercel espera uma variável chamada `app`
# Ou você pode usar `from api.index import app` no vercel.json
