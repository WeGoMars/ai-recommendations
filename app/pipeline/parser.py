# 📁 app/pipeline/parser.py

from typing import Dict, Any
from app.schemas.ai_rec_dto import RecommendationRequest

# 📁 app/pipeline/parser.py

from typing import Dict, Any
from app.schemas.ai_rec_dto import RecommendationRequest


def parse(request_data: RecommendationRequest) -> Dict[str, Any]:
    simple = request_data["simplePF"]
    stock_list = request_data["stockPF"]
    market = request_data["marketReport"]
    preference = request_data.get("userPreference", {})

    parsed = {
        "user_portfolio": {
            "total_asset_amount": simple["totalAsset"],
            "total_cash_amount": simple["cash"],
            "invested_amount": simple["investedAmount"],
            "investment_ratio": simple["investRatio"],
            "total_seed_amount": simple["totalSeed"],
            "overall_return_rate": simple["returnRate"]
        },
        "held_stocks": [
            {
                "ticker_symbol": s["symbol"],
                "company_name": s["name"],
                "number_of_shares": s["quantity"],
                "average_buy_price": s["avgBuyPrice"],
                "current_valuation": s["evalAmount"],
                "valuation_gain": s["evalGain"],
                "return_rate": s["returnRate"]
            } for s in stock_list
        ],
        "market_environment": {
            "snp500_monthly_return_percentages": {
                "description": "S&P500 수익률 (현재 시점 기준으로부터 n개월 전까지)",
                "monthly_returns": {
                    f"{k}_ago": v for k, v in market["snp500_returns"].items()
                },
                "average_return_last_12_months": sum(market["snp500_returns"].values()) / len(market["snp500_returns"])
            },
            "vix_volatility_index": {
                "description": "최근 15일간의 VIX 변동성 지수 (과거 → 최근)",
                "daily_values": market["vix"],
                "average": sum(market["vix"]) / len(market["vix"]),
                "most_recent": market["vix"][-1] if market["vix"] else None
            },
            "fed_funds_interest_rate": {
                "description": "월별 기준금리 평균 (예측 포함)",
                "monthly_average_rate": market["fedfunds_average"],
                "most_recent_three_months": list(market["fedfunds_average"].values())[-3:]
            }
        },
        "user_preference": {
            "risk_level": preference.get("riskLevel", "unknown"),
            "preferred_strategies": preference.get("preferredStrategies", []),
            "preferred_sectors": preference.get("preferredSectors", [])
        }
    }

    return parsed


def to_markdown(parsed_request: Dict[str, Any]) -> str:
    """
    파싱된 요청서(dict)를 마크다운 텍스트 형식으로 변환
    """
    md = []

    # 사용자 포트폴리오
    up = parsed_request["user_portfolio"]
    md.append("## 👤 사용자 포트폴리오 요약\n")
    md.append(f"- 총 자산: ${up['total_asset_amount']:,.2f}")
    md.append(f"- 투자 금액: ${up['invested_amount']:,.2f}")
    md.append(f"- 투자 비율: {up['investment_ratio']:.2%}")
    md.append(f"- 수익률: {up['overall_return_rate']:.2%}")
    md.append(f"- 현금 비중: {up['total_cash_amount'] / up['total_asset_amount']:.2%}\n")

    # 보유 종목
    md.append("## 📈 보유 종목 요약\n")
    for stock in parsed_request["held_stocks"]:
        md.append(f"- **{stock['ticker_symbol']} ({stock['company_name']})**: "
                  f"{stock['number_of_shares']}주, "
                  f"평균매입가 ${stock['average_buy_price']:.2f}, "
                  f"평가금액 ${stock['current_valuation']:.2f}, "
                  f"수익률 {stock['return_rate']:.2%}")

    # 시장 환경
    me = parsed_request["market_environment"]
    snp = me["snp500_monthly_return_percentages"]
    vix = me["vix_volatility_index"]
    fed = me["fed_funds_interest_rate"]

    md.append("\n## 🌐 시장 환경 요약\n")
    md.append("### 📊 S&P 500 수익률")
    md.append(f"- 설명: {snp['description']}")
    md.append(f"- 최근 12개월 평균 수익률: {snp['average_return_last_12_months']:.2f}%")

    md.append("\n### 📉 VIX 변동성")
    md.append(f"- 설명: {vix['description']}")
    md.append(f"- 최근 평균 VIX: {vix['average']:.2f}")
    md.append(f"- 최신 VIX: {vix['most_recent']:.2f}")

    md.append("\n### 💰 연준 기준금리")
    md.append(f"- 설명: {fed['description']}")
    md.append(f"- 최근 3개월: {', '.join([f'{r:.2f}%' for r in fed['most_recent_three_months']])}")
    
    
    # 사용자 선호
    upref = parsed_request["user_preference"]
    md.append("\n## 💡 사용자 선호 정보")
    md.append(f"- 리스크 허용 수준: {upref['risk_level'].capitalize()}")
    md.append(f"- 선호 전략: {', '.join(upref['preferred_strategies'])}")
    md.append(f"- 선호 섹터: {', '.join(upref['preferred_sectors'])}")

    return "\n".join(md)