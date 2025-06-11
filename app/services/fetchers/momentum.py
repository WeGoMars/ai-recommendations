from datetime import date, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.models.stock_ohlcv import StockOhlcv
from app.models.stock import Stock
from app.models.stock_financials import StockFinancials
import numpy as np
from collections import defaultdict


def normalize_score(value: float, min_val: float, max_val: float) -> float:
    if value is None:
        return 0.0
    return max(0.0, min(10.0, 10.0 * (value - min_val) / (max_val - min_val)))

def fetch_candidates_momentum(db: Session) -> List[Dict]:
    today = date.today()
    recent_start = today - timedelta(days=20)
    past_start = today - timedelta(days=40)

    subquery = (
        db.query(
            StockOhlcv.stock_id.label("stock_id"),
            case((StockOhlcv.timestamp >= recent_start, StockOhlcv.close), else_=None).label("recent_close"),
            case(((StockOhlcv.timestamp < recent_start) & (StockOhlcv.timestamp >= past_start), StockOhlcv.close), else_=None).label("past_close")
        )
        .filter(StockOhlcv.interval == '1day', StockOhlcv.timestamp >= past_start)
        .subquery()
    )

    avg_query = (
        db.query(subquery.c.stock_id,
                 func.avg(subquery.c.recent_close).label("recent_avg"),
                 func.avg(subquery.c.past_close).label("past_avg"))
        .group_by(subquery.c.stock_id)
        .having(func.count(subquery.c.recent_close) >= 10)
        .having(func.count(subquery.c.past_close) >= 10)
        .all()
    )

    momentum_scores = []
    for row in avg_query:
        if row.recent_avg and row.past_avg and row.past_avg > 0:
            price_change = (row.recent_avg / row.past_avg) - 1
            momentum_scores.append((row.stock_id, price_change))

    top_15_ids = sorted(momentum_scores, key=lambda x: x[1], reverse=True)[:15]
    top_stock_ids = [s[0] for s in top_15_ids]
    momentum_map = {s[0]: s[1] for s in top_15_ids}

    ohlcv_rows = (
        db.query(StockOhlcv.stock_id, StockOhlcv.timestamp, StockOhlcv.close)
        .filter(StockOhlcv.stock_id.in_(top_stock_ids),
                StockOhlcv.interval == '1day',
                StockOhlcv.timestamp >= recent_start)
        .all()
    )

    price_map = defaultdict(list)
    for row in sorted(ohlcv_rows, key=lambda r: (r.stock_id, r.timestamp)):
        price_map[row.stock_id].append(row.close)

    volatility_map = {}
    for stock_id, closes in price_map.items():
        if len(closes) >= 2:
            returns = np.diff(closes) / closes[:-1]
            volatility_map[stock_id] = float(np.std(returns))

    results = (
        db.query(Stock, StockFinancials)
        .join(StockFinancials, Stock.id == StockFinancials.stock_id)
        .filter(Stock.id.in_(top_stock_ids))
        .all()
    )

    candidates = []
    for stock, fin in results:
        stock_id = stock.id
        price_change = momentum_map.get(stock_id)
        volatility = volatility_map.get(stock_id)
        market_cap = fin.marketCap

        score = 0.0
        metrics = []

        if price_change is not None:
            norm_score = normalize_score(price_change, 0.0, 0.5)
            s = norm_score * 0.6
            score += s
            metrics.append({
                "name": "price_change_3m",
                "value": round(price_change * 100, 2),
                "score": round(s, 2)
            })

        if volatility is not None:
            norm_score = normalize_score(0.1 - volatility, 0.0, 0.1)
            s = norm_score * 0.2
            score += s
            metrics.append({
                "name": "volatility",
                "value": round(volatility * 100, 2),
                "score": round(s, 2)
            })

        if market_cap is not None:
            norm_score = normalize_score(market_cap / 1e12, 0.0, 1.0)
            s = norm_score * 0.2
            score += s
            metrics.append({
                "name": "market_cap",
                "value": round(market_cap, 2),
                "score": round(s, 2)
            })

        candidates.append({
            "symbol": stock.symbol,
            "name": stock.name,
            "sector": stock.sector,
            "industry": stock.industry,
            "score": round(score, 4),
            "metrics": metrics
        })

    return sorted(candidates, key=lambda x: x["score"], reverse=True)
