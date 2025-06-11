# 📁 app/pipeline/analyst.py

from typing import List, Dict
from app.services import fetcher

def analyze(selected_strategies: List[Dict]) -> List[Dict]:
    all_scored_stocks = []

    for strategy in selected_strategies:
        strategy_name = strategy["name"]
        criteria = get_strategy_criteria(strategy_name)

        # 1. DB 또는 서비스에서 해당 전략용 후보 종목 리스트 로딩
        candidates = fetcher.fetch_candidates(strategy_name, criteria)

        # 2. 각 종목의 평가 지표 조회 및 점수 계산
        for stock in candidates:
            stock_score = evaluate_stock(stock, criteria)
            stock["score"] = stock_score
            stock["strategy"] = strategy_name
            all_scored_stocks.append(stock)

    return all_scored_stocks


def get_strategy_criteria(strategy_name: str) -> List[Dict]:
    from strategies.definitions import strategy_definitions
    return next((s["evaluation_criteria"] for s in strategy_definitions if s["name"] == strategy_name), [])


def evaluate_stock(stock: Dict, criteria: List[Dict]) -> float:
    score = 0.0
    for criterion in criteria:
        name = criterion["name"]
        weight = criterion["weight"]
        value = stock.get(name)
        if value is not None:
            score += weight * value
    return score
 