from typing import List, TypedDict, Dict





#############REQUESTS
class UserPortfolioDto(TypedDict):
    totalAsset: float
    investedAmount: float
    evalGain: float
    returnRate: float
    totalSeed: float
    investRatio: float
    cash: float


class StockPortfolioDto(TypedDict):
    symbol: str
    name: str
    quantity: int
    avgBuyPrice: float
    evalAmount: float
    evalGain: float
    returnRate: float


class RecommendationRequest(TypedDict):
    simplePF: UserPortfolioDto
    stockPF: List[StockPortfolioDto]
    marketReport: Dict  # 자유 형식: snp500_returns, vix, fedfunds_average 등 포함

#############RESPONSES


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
