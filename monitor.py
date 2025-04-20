from flask import jsonify

def healthcheck():
    """
    Verifica se a API está no ar.
    ---
    tags:
      - Monitoramento
    responses:
      200:
        description: API funcionando corretamente
        schema:
          type: object
          properties:
            status:
              type: string
              example: ok
    """
    return jsonify({"status": "ok"}), 200
