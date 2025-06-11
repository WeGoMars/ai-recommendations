import importlib
from sqlalchemy.orm import Session
from app.strategies.definitions import strategy_definitions
import traceback

# 전략 이름에서 fetcher 함수 매핑 (초기화 시점에)
_strategy_fetcher_map = {}

print(f"[DEBUG] 전략 목록 초기화 중...")

for strat in strategy_definitions:
    name = strat["name"]
    try:
        print(f"[DEBUG] importing fetcher for strategy: {name}")
        module = importlib.import_module(f"app.services.fetchers.{name}")
        func = getattr(module, f"fetch_candidates_{name}")
        _strategy_fetcher_map[name] = func
        print(f"[✅] 등록 완료: {name}")
    except (ImportError, AttributeError) as e:
        print(f"⚠️ 전략 '{name}'에 대한 fetcher 모듈/함수 누락: {e}")
        traceback.print_exc()

def fetch_candidates_for_strategy(strategy_name: str, db: Session):
    fetcher = _strategy_fetcher_map.get(strategy_name)
    if not fetcher:
        raise ValueError(f"전략 '{strategy_name}'에 대한 fetcher 함수가 등록되지 않았습니다.")
    return fetcher(db)
