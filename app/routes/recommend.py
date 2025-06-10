from flask import Blueprint, jsonify, request

recommend_bp = Blueprint("recommend", __name__, url_prefix="/recommend")

@recommend_bp.route("/", methods=["POST"])
def recommend():
    data = request.get_json()
    print("받은 데이터:", data)
    return jsonify({"status": "received", "preview": data})