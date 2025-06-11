from typing import List, Dict, Any

class RecommendationContext:
    def __init__(self, original_data: Dict):
        self.original_request: Dict = original_data
        self.parsed_request: Dict = {}
        self.request_markdown: str = ""
        
        self.selected_strategies: List[Dict] = []
        
        self.scored_candidates: List[Dict] = []
        
        self.final_stocks: List[Dict] = []

    def debug(self):
        return {
            "parsed_request": self.parsed_request,
            "request_markdown": self.request_markdown,
            "selected_strategies": [s["name"] for s in self.selected_strategies],
            "scored_candidates": [
                {
                    "symbol": s["symbol"],
                    "score": s["score"],
                    "metrics": s.get("metrics", []),
                    "reasons": s.get("reasons", [])
                }
                for s in self.scored_candidates
            ],
            "final_stocks": [s["symbol"] for s in self.final_stocks]
        }
