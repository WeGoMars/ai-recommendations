from typing import List, TypedDict


class Reason(TypedDict):
    type: str         # "strategy" | "metric" | "commentary"
    detail: str       # 자연어 설명
    score: float      # 해당 항목의 점수


class RecommendedStock(TypedDict):
    symbol: str
    name: str
    sector: str
    industry: str
    score: float            # 총점 (reason 점수 합계)
    reasons: List[Reason]


class RecommendationResponse(TypedDict):
    recommended: List[RecommendedStock]
