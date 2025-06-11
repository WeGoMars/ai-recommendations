from typing import Dict, List
import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.schemas.ai_rec_dto import RecommendationResponse

load_dotenv()
llm = ChatOpenAI(model="gpt-4o", temperature=0.5)

def extract_top_candidates_summary(context, top_k: int = 5) -> List[Dict]:
    result = []
    for stock in context.scored_candidates[:top_k]:
        result.append({
            "symbol": stock["symbol"],
            "name": stock.get("name", ""),
            "sector": stock.get("sector", ""),
            "score": stock["score"],
            "top_metrics": sorted(
                [
                    {"name": m["name"], "score": m["score"], "value": m.get("value")}
                    for m in stock["metrics"]
                ],
                key=lambda x: x["score"],
                reverse=True
            )[:3],
            "strategies": [
                {"description": r["detail"], "score": r["score"]}
                for r in stock["reasons"]
                if r["type"] == "strategy"
            ]
        })
    return result

def format_prompt_input(context) -> Dict:
    return {
        "portfolio_summary": context.request_markdown,
        "strategy_explanations": "\n".join([
            f"- {s['name']}: {s['reason']}" for s in context.selected_strategies
        ]),
        "top_candidates_json": json.dumps(
            extract_top_candidates_summary(context),
            indent=2,
            ensure_ascii=False
        )
    }

def comment(context) -> RecommendationResponse:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 금융 투자 전략가이며, AI 종목 추천 시스템의 해설가입니다."),
        ("user", """아래는 사용자의 포트폴리오 정보 및 시장 분석 결과입니다.

{portfolio_summary}

사용자는 다음과 같은 전략을 기반으로 종목 추천을 받았습니다:
{strategy_explanations}

추천 종목 상위 5개의 요약은 다음과 같습니다:
{top_candidates_json}

위 정보를 바탕으로, 각 종목의 추천 사유를 바탕으로 종합 평가 코멘트를 작성해주세요.
각 종목별로 2~3문장 이내로, 전략적 강점, 기대 효과, 유의할 점 등을 간단히 설명해주세요.

결과는 아래와 같은 JSON 배열로 반환해주세요:

[
  {{ "symbol": "AAPL", "comment": "이 종목은 안정적인 실적과 낮은 변동성을 바탕으로 장기 투자에 적합합니다." }},
  ...
]
""")
    ])

    variables = format_prompt_input(context)
    messages = prompt.format_messages(**variables)
    response = llm.invoke(messages)

    try:
        content = response.content
        if "```json" in content:
            import re
            match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
            if match:
                content = match.group(1)
        comment_data = json.loads(content)
    except Exception as e:
        print(f"❗ LLM 응답 파싱 오류: {e}")
        comment_data = []

    # 코멘트 결과를 context.scored_candidates에 주입
    comment_map = {c["symbol"]: c["comment"] for c in comment_data}
    final = []
    for stock in context.scored_candidates:
        symbol = stock["symbol"]
        commentary = comment_map.get(symbol)
        if commentary:
            stock["reasons"].append({
                "type": "commentary",
                "detail": commentary
            })
        final.append(stock)

    context.final_stocks = final

    return RecommendationResponse(stocks=final)
