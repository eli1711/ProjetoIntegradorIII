# app/routers/test_routes.py
from flask import Blueprint

test_bp = Blueprint('test_bp', __name__)

@test_bp.route('/api/ping', methods=['GET'])
def ping():
    return {"message": "pong"}, 200
