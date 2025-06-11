# 📁 app/services/recommend_service.py

from typing import Dict
from app.pipeline import parser,strategist
# analyst, commenter
from app.schemas.ai_rec_dto import RecommendationRequest, RecommendationResponse
from app.models.context import RecommendationContext

def handle_recommendation_request(data: Dict) -> RecommendationResponse:
    context = RecommendationContext(data)
    # 1. 파싱
    print("🔍 [1/4] 파서 실행 중...")
    context.parsed_request = parser.parse(data)
    context.request_markdown = parser.to_markdown(context.parsed_request)

    # 2. 전략 선택
    print("🧠 [2/4] 전략 선정 중...")
    context.selected_strategies = strategist.select_strategies(context.request_markdown,context.parsed_request)
    # print(context.selected_strategies)

    # # 3. 종목 분석
    print("📊 [3/4] 종목 분석 중...")
    context.scored_candidates = analyst.analyze(context.selected_strategies)

    # # 4. 코멘트 생성 및 응답 가공
    # print("🗣️ [4/4] 코멘터리 생성 중...")
    # response = commenter.build_response(top_stocks, selected_strategies)

    # return response
