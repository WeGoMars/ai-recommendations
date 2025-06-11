from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from sqlalchemy.orm import aliased
from app.models.stock import Stock
from app.models.stock_financials import StockFinancials
from app.models.stock_ohlcv import StockOhlcv

def normalize_score(value: float, min_val: float, max_val: float) -> float:
    if value is None:
        return 0.0
    return max(0.0, min(10.0, 10.0 * (value - min_val) / (max_val - min_val)))

def fetch_candidates_value_stability(db: Session) -> List[Dict]:
    weights = {
        "earning_yield": 0.4,
        "book_yield": 0.3,
        "roe": 0.3
    }

    # Step 1: 가장 최근 주가 가져오기
    latest_dates_subq = (
        db.query(
            StockOhlcv.stock_id,
            func.max(StockOhlcv.timestamp).label("latest_date")
        )
        .filter(StockOhlcv.interval == "1day")
        .group_by(StockOhlcv.stock_id)
        .subquery()
    )

    ohlcv_alias = aliased(StockOhlcv)
    latest_prices_query = (
        db.query(ohlcv_alias.stock_id, ohlcv_alias.close)
        .join(
            latest_dates_subq,
            and_(
                ohlcv_alias.stock_id == latest_dates_subq.c.stock_id,
                ohlcv_alias.timestamp == latest_dates_subq.c.latest_date
            )
        )
        .all()
    )
    latest_prices = {row.stock_id: row.close for row in latest_prices_query}

    # Step 2: 재무정보 기반 계산
    results = (
        db.query(Stock, StockFinancials)
        .join(StockFinancials, Stock.id == StockFinancials.stock_id)
        .filter(
            StockFinancials.eps != None,
            StockFinancials.bps != None,
            StockFinancials.roe != None
        )
        .all()
    )

    candidates = []
    for stock, fin in results:
        stock_id = stock.id
        price = latest_prices.get(stock_id)
        if price is None or price <= 0:
            continue

        score = 0.0
        metrics = []

        # earning_yield (정규화: 0 ~ 0.12)
        earning_yield = fin.eps / price
        norm = normalize_score(earning_yield, 0.0, 0.12)
        s = norm * weights["earning_yield"]
        score += s
        metrics.append({
            "name": "earning_yield", "value": round(earning_yield, 6), "score": round(s, 2)
        })

        # book_yield (정규화: 0 ~ 1.0)
        book_yield = fin.bps / price
        norm = normalize_score(book_yield, 0.0, 1.0)
        s = norm * weights["book_yield"]
        score += s
        metrics.append({
            "name": "book_yield", "value": round(book_yield, 6), "score": round(s, 2)
        })

        # ROE (정규화: 0 ~ 0.30)
        norm = normalize_score(fin.roe, 0.0, 0.30)
        s = norm * weights["roe"]
        score += s
        metrics.append({
            "name": "roe", "value": round(fin.roe, 3), "score": round(s, 2)
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
