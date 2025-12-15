from flask import Blueprint

test_bp = Blueprint('test', __name__, url_prefix='/api')

@test_bp.route('/ping', methods=['GET'])
def ping():
    return {"message": "pong"}, 200
