strategy_definitions = [
    {
        "name": "dividend_stability",
        "description": "배당 수익률이 높고 실적이 안정적인 기업에 투자하는 전략입니다. 예측 가능한 현금흐름을 선호하는 안정 성향의 투자자에게 적합합니다.",
        "when_to_use": (
            "사용자의 리스크 허용 수준이 'low'이고, 시장 변동성(VIX)이 20 이하로 안정적인 경우. "
            "현금 보유 비중이 높고, 꾸준한 배당을 통해 수익을 확보하려는 상황에 유리합니다."
        ),
        "evaluation_criteria": [
            {"name": "dividend_yield", "description": "배당 수익률", "weight": 0.5},
            {"name": "debt_ratio", "description": "부채비율", "weight": -0.2},
            {"name": "roe", "description": "자기자본이익률", "weight": 0.3}
        ]
    },
    {
        "name": "portfolio_balance",
        "description": "자산군과 섹터의 균형 잡힌 분산 투자를 통해 리스크를 완화하는 전략입니다.",
        "when_to_use": (
            "사용자의 리스크 허용 수준이 'high'이고, 투자 비중이 지나치게 낮거나 높으며 특정 섹터에 과도하게 편중된 경우. "
            "자산 리밸런싱을 통해 안정성을 높이려는 상황에서 적합합니다."
        ),
        "evaluation_criteria": [
                {"name": "beta", "description": "시장 민감도", "weight": -0.25},
                {"name": "current_ratio", "description": "유동비율", "weight": 0.25},
                {"name": "roe", "description": "자기자본이익률", "weight": 0.25},
                {"name": "preferred_sector_score", "description": "사용자 선호 섹터 여부", "weight": 0.15},
                {"name": "underweighted_sector_score", "description": "보유 비중이 낮은 섹터 여부", "weight": 0.10}
            ]
    },
    {
        "name": "value_stability",
        "description": "실적(EPS)과 자산(BPS) 기준으로 저평가된 종목을 발굴하여 안정적인 수익을 추구하는 가치 투자 전략입니다.",
        "when_to_use": (
            "사용자의 리스크 허용 수준이 'medium' 이하이며, 변동성 높은 시장에서도 안정적인 내재 가치를 바탕으로 투자하고자 할 때 유용합니다. "
            "특히 실적 대비 시가총액이 낮거나 자산 대비 저평가된 종목에 관심이 있을 때 적합합니다."
        ),
        "evaluation_criteria": [
            {"name": "earning_yield_score", "description": "EPS 대비 시가총액 비율 (높을수록 저평가)", "weight": 0.4},
            {"name": "book_yield_score", "description": "BPS 대비 시가총액 비율 (높을수록 저평가)", "weight": 0.3},
            {"name": "roe", "description": "자기자본이익률 (높을수록 우량)", "weight": 0.3}
        ]
    },
    {
        "name": "momentum",
        "description": "최근 상승 흐름을 보이는 종목에 투자하여 시장의 탄력을 활용하는 전략입니다.",
        "when_to_use": (
            "사용자의 리스크 허용 수준이 'high'이고, S&P500의 최근 1~3개월 수익률이 높으며 시장 전반에 긍정적인 분위기가 형성되어 있는 경우."
        ),
        "evaluation_criteria": [
            {"name": "price_change_3m", "description": "3개월 주가 상승률", "weight": 0.6},
            {"name": "volatility", "description": "변동성 (짧은 기간 기준)", "weight": -0.2},
            {"name": "market_cap", "description": "시가총액 (대형주 선호)", "weight": 0.2}
        ]
    },
    {
        "name": "sector_rotation",
        "description": "유망한 섹터로 포지션을 옮기며 트렌드에 올라타는 전략입니다.",
        "when_to_use": (
            "사용자의 리스크 허용 수준이 'high'이고, 섹터별 수익률 차이가 뚜렷하며 "
            "현재 보유 종목의 섹터와 사용자의 선호 섹터 간 불일치가 존재할 때."
        ),
        "evaluation_criteria": [
            {"name": "sector_trend_score", "description": "최근 5일간 섹터 평균 수익률", "weight": 0.5},
            {"name": "price_change_1m", "description": "1개월 주가 수익률", "weight": 0.3},
            {"name": "volatility", "description": "단기 주가 변동성", "weight": 0.2}
        ]
    },
    {
        "name": "rebound_buy",
        "description": "최근 하락한 종목 중 반등 가능성이 있는 종목을 선별하는 전략입니다.",
        "when_to_use": (
            "S&P500이 최근 하락세에 있지만 장기 흐름은 우상향이며, "
            "사용자의 리스크 허용 수준이 'high'로 전환점을 노리고자 하는 경우."
        ),
        "evaluation_criteria": [
            {"name": "drawdown", "description": "최근 고점 대비 낙폭률", "weight": 0.5},
            {"name": "price_change_1m", "description": "1개월 주가 수익률", "weight": -0.3},
            {"name": "roe", "description": "자기자본이익률", "weight": 0.2}
        ]
    }
]
