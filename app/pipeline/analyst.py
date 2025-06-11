from typing import List, Dict
from flask import g
from app.services.fetchers import fetch_candidates_for_strategy
from typing import List, Dict
from flask import g
from app.services.fetchers import fetch_candidates_for_strategy

# 전략 내 랭킹별 점수: 1등 20점, 2등 19점, ..., 최소 1점
def generate_rank_points(n: int) -> List[int]:
    return [max(1, 20 - i) for i in range(n)]

def analyze(strategy_list: List[Dict], top_n: int = 4) -> List[Dict]:
    """
    전략 리스트를 받아, 종합된 추천 종목 리스트를 반환.
    각 종목은 score, reasons, metrics 등을 포함.    
    중복 종목은 symbol 기준으로 통합 처리됨.
    점수는 전략 내 랭킹 기반으로 부여됨.
    """
    merged_candidates: Dict[str, Dict] = {}

    for strategy in strategy_list:
        strategy_name = strategy["name"]
        strategy_reason = strategy["reason"]

        try:
            candidates = fetch_candidates_for_strategy(strategy_name, g.db)
        except Exception as e:
            print(f"❌ 전략 '{strategy_name}' 후보 조회 실패: {e}")
            continue

        ranked = sorted(candidates, key=lambda x: x["score"], reverse=True)
        rank_points = generate_rank_points(len(ranked))

        for i, c in enumerate(ranked):
            symbol = c["symbol"]
            rank_score = rank_points[i]
            reason_obj = {
                "type": "strategy",
                "detail": f"{strategy_name.replace('_', ' ').title()} 전략: {strategy_reason}",
                "score": rank_score
            }

            if symbol in merged_candidates:
                merged_candidates[symbol]["score"] += rank_score
                merged_candidates[symbol]["reasons"].append(reason_obj)
            else:
                merged_candidates[symbol] = {
                    "symbol": c["symbol"],
                    "name": c["name"],
                    "sector": c["sector"],
                    "industry": c["industry"],
                    "score": rank_score,
                    "metrics": c.get("metrics", []),
                    "reasons": [reason_obj]
                }

    result = list(merged_candidates.values())
    return sorted(result, key=lambda x: x["score"], reverse=True)[:top_n]
