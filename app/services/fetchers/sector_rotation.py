from typing import List, Dict
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import defaultdict
import numpy as np

from app.models.stock import Stock
from app.models.stock_financials import StockFinancials
from app.models.stock_ohlcv import StockOhlcv
from app.models.sector_performance import SectorPerformance

def normalize_score(value: float, min_val: float, max_val: float) -> float:
    if value is None:
        return 0.0
    return max(0.0, min(10.0, 10.0 * (value - min_val) / (max_val - min_val)))

def fetch_candidates_sector_rotation(db: Session) -> List[Dict]:
    weights = {
        "sector_trend_score": 0.5,
        "price_change_1m": 0.3,
        "volatility": 0.2
    }

    today = date.today()
    start_date = today - timedelta(days=5)
    one_month_ago = today - timedelta(days=30)

    # Step 1: 섹터별 평균 수익률 → 상위 3개 섹터 선정
    sector_returns = (
        db.query(
            SectorPerformance.sector,
            func.avg(SectorPerformance.return_).label("avg_return")
        )
        .filter(SectorPerformance.date >= start_date)
        .group_by(SectorPerformance.sector)
        .all()
    )
    top_sectors = [s[0] for s in sorted(sector_returns, key=lambda x: x[1], reverse=True)[:3]]
    sector_return_map = {s[0]: s[1] for s in sector_returns}

    # Step 2: 해당 섹터의 종목 조회
    results = (
        db.query(Stock, StockFinancials)
        .join(StockFinancials, Stock.id == StockFinancials.stock_id)
        .filter(Stock.sector.in_(top_sectors))
        .all()
    )
    stock_map = {stock.id: (stock, fin) for stock, fin in results}

    # Step 3: OHLCV 기반 수익률 및 변동성 계산
    ohlcv_rows = (
        db.query(StockOhlcv.stock_id, StockOhlcv.timestamp, StockOhlcv.close)
        .filter(
            StockOhlcv.stock_id.in_(stock_map.keys()),
            StockOhlcv.interval == "1day",
            StockOhlcv.timestamp >= one_month_ago
        ).all()
    )

    price_map = defaultdict(list)
    for row in sorted(ohlcv_rows, key=lambda r: (r.stock_id, r.timestamp)):
        price_map[row.stock_id].append((row.timestamp, row.close))

    candidates = []
    for stock_id, price_series in price_map.items():
        if len(price_series) < 5:
            continue

        stock, fin = stock_map[stock_id]
        prices = [p[1] for p in price_series]
        if not prices or prices[0] == 0:
            continue

        price_change_1m = (prices[-1] / prices[0]) - 1  # 수익률
        returns = np.diff(prices) / prices[:-1]         # 일일 수익률
        volatility = float(np.std(returns))             # 표준편차

        sector_trend_score = sector_return_map.get(stock.sector, 0)

        score = 0.0
        metrics = []

        s1 = normalize_score(sector_trend_score, 0.0, 0.05) * weights["sector_trend_score"]
        score += s1
        metrics.append({
            "name": "sector_trend_score",
            "value": round(sector_trend_score * 100, 2),
            "score": round(s1, 2)
        })

        s2 = normalize_score(price_change_1m, 0.0, 0.2) * weights["price_change_1m"]
        score += s2
        metrics.append({
            "name": "price_change_1m",
            "value": round(price_change_1m * 100, 2),
            "score": round(s2, 2)
        })

        s3 = normalize_score(volatility, 0.0, 0.05) * weights["volatility"]
        score += s3
        metrics.append({
            "name": "volatility",
            "value": round(volatility * 100, 2),
            "score": round(s3, 2)
        })

        candidates.append({
            "symbol": stock.symbol,
            "name": stock.name,
            "sector": stock.sector,
            "industry": stock.industry,
            "score": round(score, 4),
            "metrics": metrics
        })

    return sorted(candidates, key=lambda x: x["score"], reverse=True)[:12]
