from flask import Flask, g
from app.pipeline import analyst
from app.core.database import SessionLocal
import pprint

# ✅ Flask App Context 열기
app = Flask(__name__)

with app.app_context():
    # 🔹 DB 세션 등록
    g.db = SessionLocal()

    # 🔹 더미 포트폴리오 context 삽입 (portfolio_balance용)
    g.context = {
        "held_stocks": [
            {"ticker_symbol": "AAPL", "sector": "Technology"},
            {"ticker_symbol": "A", "sector": "Healthcare"}
        ],
        "user_preference": {
            "preferred_sectors": ["Utilities", "Energy", "Financial Services"]
        }
    }

    # 🔹 전략 리스트 (6개 전체)
    strategy_list = [
        {"name": "portfolio_balance", "reason": "포트폴리오 균형 조정 필요"},
        {"name": "momentum", "reason": "상승장세에서 탄력 투자"},
        {"name": "sector_rotation", "reason": "섹터 순환 트렌드 대응"},
        {"name": "value_stability", "reason": "저평가 우량주 선호"},
        {"name": "dividend_stability", "reason": "안정적인 배당 기반 투자"},
        {"name": "rebound_buy", "reason": "낙폭과대 반등 기대"}
    ]

    print("🔍 전략 통합 분석 실행 중...")
    scored = analyst.analyze(strategy_list)

    print(f"\n✅ 총 추천 종목 수: {len(scored)}")
    for stock in scored[:5]:
        print(f"\n⭐ {stock['symbol']} / {stock['score']}점")
        pprint.pprint(stock["metrics"], indent=2)
        for reason in stock["reasons"]:
            print(f"  ➤ {reason['type']}: {reason['detail']} ({reason['score']})")
