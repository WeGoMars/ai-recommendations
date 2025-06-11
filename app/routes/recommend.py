from flask import Blueprint, jsonify, request, Response
import json
from app.services.recommend_service import handle_recommendation_request


recommend_bp = Blueprint("recommend", __name__, url_prefix="/recommend")


@recommend_bp.route("/", methods=["POST"])
def recommend():
    try:
        data = request.get_json()
        # print("📩 받은 요청 데이터:", data)

        # 서비스 계층 호출
        result = handle_recommendation_request(data)

        return Response(
            json.dumps(result, ensure_ascii=False),
            content_type="application/json; charset=utf-8"
        ), 200
    
    except Exception as e:
        print("❌ 오류 발생:", e)
        return jsonify({"error": str(e)}), 500