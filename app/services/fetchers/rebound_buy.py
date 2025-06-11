from typing import List, Dict
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import defaultdict
import numpy as np

from app.models.stock import Stock
from app.models.stock_financials import StockFinancials
from app.models.stock_ohlcv import StockOhlcv

def normalize_score(value: float, min_val: float, max_val: float) -> float:
    if value is None:
        return 0.0
    return max(0.0, min(10.0, 10.0 * (value - min_val) / (max_val - min_val)))

def fetch_candidates_rebound_buy(db: Session) -> List[Dict]:
    weights = {
        "drawdown": 0.5,
        "price_change_1m": 0.3,
        "roe": 0.2
    }

    today = date.today()
    start_90 = today - timedelta(days=90)
    start_30 = today - timedelta(days=30)

    ohlcv_rows = (
        db.query(StockOhlcv.stock_id, StockOhlcv.timestamp, StockOhlcv.close)
        .filter(
            StockOhlcv.interval == "1day",
            StockOhlcv.timestamp >= start_90
        )
        .all()
    )

    price_map = defaultdict(list)
    for row in sorted(ohlcv_rows, key=lambda r: (r.stock_id, r.timestamp)):
        price_map[row.stock_id].append((row.timestamp, row.close))

    stock_results = (
        db.query(Stock, StockFinancials)
        .join(StockFinancials, Stock.id == StockFinancials.stock_id)
        .all()
    )
    stock_map = {s.id: (s, f) for s, f in stock_results}

    candidates = []
    for stock_id, series in price_map.items():
        if stock_id not in stock_map or len(series) < 10:
            continue

        closes = [p[1] for p in series]
        timestamps = [p[0] for p in series]

        close_now = closes[-1]
        max_close = max(closes)
        close_30_days_ago = next((c for t, c in series if t >= start_30), None)

        if not close_now or not max_close or not close_30_days_ago or close_30_days_ago == 0:
            continue

        drawdown = (close_now / max_close) - 1
        price_change_1m = (close_now / close_30_days_ago) - 1

        stock, fin = stock_map[stock_id]

        score = 0.0
        metrics = []

        s1_raw = normalize_score(drawdown, -0.5, 0.0)
        s1 = s1_raw * weights["drawdown"]
        score += s1
        metrics.append({
            "name": "drawdown", "value": round(drawdown * 100, 2), "score": round(s1, 2)
        })

        s2_raw = normalize_score(price_change_1m, -0.2, 0.1)
        s2 = s2_raw * weights["price_change_1m"]
        score += s2
        metrics.append({
            "name": "price_change_1m", "value": round(price_change_1m * 100, 2), "score": round(s2, 2)
        })

        s3 = 0.0
        if fin.roe is not None:
            s3_raw = normalize_score(fin.roe, 0.0, 0.3)
            s3 = s3_raw * weights["roe"]
            score += s3
            metrics.append({
                "name": "roe", "value": round(fin.roe, 2), "score": round(s3, 2)
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
