from typing import List, Dict
from sqlalchemy.orm import Session
from app.models.stock import Stock
from app.models.stock_financials import StockFinancials

def normalize_score(value: float, min_val: float, max_val: float, invert: bool = False) -> float:
    if value is None:
        return 0.0
    clipped = max(min(value, max_val), min_val)
    ratio = (clipped - min_val) / (max_val - min_val)
    score = 10.0 * (1.0 - ratio) if invert else 10.0 * ratio
    return round(score, 2)

def fetch_candidates_dividend_stability(db: Session) -> List[Dict]:
    results = (
        db.query(Stock, StockFinancials)
        .join(StockFinancials, Stock.id == StockFinancials.stock_id)
        .filter(StockFinancials.dividendYield != None)
        .filter(StockFinancials.dividendYield > 0)
        .all()
    )

    weights = {
        "dividend_yield": 0.5,
        "debt_ratio": 0.2,     # 뒤집어서 낮을수록 좋게 처리됨
        "roe": 0.3
    }

    candidates = []
    for stock, fin in results:
        score = 0.0
        metrics = []

        # 배당 수익률 정규화 (0~10%)
        if fin.dividendYield is not None:
            norm = normalize_score(fin.dividendYield, 0.0, 0.1)
            s = norm * weights["dividend_yield"]
            score += s
            metrics.append({
                "name": "dividend_yield", "value": round(fin.dividendYield, 4), "score": round(s, 2)
            })

        # 부채비율 (낮을수록 좋음, 0~100%)
        if fin.debtRatio is not None:
            norm = normalize_score(fin.debtRatio / 100.0, 0.0, 1.0, invert=True)
            s = norm * weights["debt_ratio"]
            score += s
            metrics.append({
                "name": "debt_ratio", "value": round(fin.debtRatio, 2), "score": round(s, 2)
            })

        # ROE 정규화 (0~50%)
        if fin.roe is not None:
            norm = normalize_score(fin.roe, 0.0, 0.5)
            s = norm * weights["roe"]
            score += s
            metrics.append({
                "name": "roe", "value": round(fin.roe, 3), "score": round(s, 2)
            })

        if metrics:
            candidates.append({
                "symbol": stock.symbol,
                "name": stock.name,
                "sector": stock.sector,
                "industry": stock.industry,
                "score": round(score, 4),
                "metrics": metrics
            })

    return sorted(candidates, key=lambda x: x["score"], reverse=True)[:12]
