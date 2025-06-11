from datetime import date, timedelta
from typing import List, Dict
from flask import g
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.sector_performance import SectorPerformance
from app.models.stock import Stock
from app.models.stock_financials import StockFinancials

def normalize_score(value: float, min_val: float, max_val: float) -> float:
    if value is None:
        return 0.0
    return max(0.0, min(10.0, 10.0 * (value - min_val) / (max_val - min_val)))

def fetch_candidates_portfolio_balance(db: Session) -> List[Dict]:
    today = date.today()
    start_date = today - timedelta(days=5)

    user_sectors = {s["sector"] for s in g.context["held_stocks"]}
    preferred_sectors = set(g.context["user_preference"]["preferred_sectors"])

    rows = (
        db.query(
            SectorPerformance.sector,
            func.avg(SectorPerformance.return_).label("avg_return")
        )
        .filter(SectorPerformance.date >= start_date)
        .group_by(SectorPerformance.sector)
        .all()
    )

    sector_scores = []
    for row in rows:
        sector = row.sector
        avg_return = row.avg_return or 0.0

        score = (
            avg_return * 0.4 +
            (1.0 if sector in preferred_sectors else 0.0) * 0.3 +
            (1.0 if sector not in user_sectors else 0.0) * 0.3
        )

        sector_scores.append((sector, score))

    top_3_sectors = [s[0] for s in sorted(sector_scores, key=lambda x: x[1], reverse=True)[:3]]

    weights = {
        "beta": 0.25,  # 변동성 낮을수록 좋음 (반전된 정규화)
        "current_ratio": 0.25,
        "roe": 0.25,
        "preferred_sector_score": 0.15,
        "underweighted_sector_score": 0.10
    }

    results = (
        db.query(Stock, StockFinancials)
        .join(StockFinancials, Stock.id == StockFinancials.stock_id)
        .filter(Stock.sector.in_(top_3_sectors))
        .all()
    )

    candidates = []
    for stock, fin in results:
        score = 0.0
        metrics = []

        if fin.beta is not None:
            beta_score = normalize_score(2.0 - fin.beta, 0.0, 2.0)
            s = beta_score * weights["beta"]
            score += s
            metrics.append({"name": "beta", "value": round(fin.beta, 3), "score": round(s, 2)})

        if fin.currentRatio is not None:
            cr_score = normalize_score(fin.currentRatio, 0.0, 20.0)
            s = cr_score * weights["current_ratio"]
            score += s
            metrics.append({"name": "current_ratio", "value": round(fin.currentRatio, 3), "score": round(s, 2)})

        if fin.roe is not None:
            roe_score = normalize_score(fin.roe, 0.0, 0.3)
            s = roe_score * weights["roe"]
            score += s
            metrics.append({"name": "roe", "value": round(fin.roe, 3), "score": round(s, 2)})

        preferred_score = 1.0 if stock.sector in preferred_sectors else 0.0
        s = preferred_score * weights["preferred_sector_score"]
        score += s
        metrics.append({"name": "preferred_sector_score", "value": preferred_score, "score": round(s, 2)})

        underweighted_score = 1.0 if stock.sector not in user_sectors else 0.0
        s = underweighted_score * weights["underweighted_sector_score"]
        score += s
        metrics.append({"name": "underweighted_sector_score", "value": underweighted_score, "score": round(s, 2)})

        candidates.append({
            "symbol": stock.symbol,
            "name": stock.name,
            "sector": stock.sector,
            "industry": stock.industry,
            "score": round(score, 4),
            "metrics": metrics
        })

    return sorted(candidates, key=lambda x: x["score"], reverse=True)[:12]
