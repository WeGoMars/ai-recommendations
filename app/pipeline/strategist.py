from typing import List, Dict
import json
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from strategies.definitions import strategy_definitions

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0)

def select_strategies(markdown_doc: str, parsed_request: Dict) -> List[Dict]:
    formatted_strategy_list = format_strategy_definitions(strategy_definitions)

    example_response = """
[
  {{
    "name": "dividend_stability",
    "reason": "시장 변동성이 낮고, 사용자의 리스크 성향이 안정적이며 현금 비중이 높기 때문입니다."
  }},
  {{
    "name": "portfolio_balance",
    "reason": "투자 종목 수가 적고 섹터 집중도가 높아 분산이 필요한 상황입니다."
  }},
  {{
    "name": "value_stability",
    "reason": "시장이 안정적이며, 저평가 우량주 선별을 통한 장기 투자 전략이 적합해 보입니다."
  }}
]
""".strip()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 금융 전략가입니다. 사용자의 투자 성향과 시장 환경에 따라 가장 적합한 전략을 추천해야 합니다."),
        ("user", f"""다음은 사용자 요청서입니다:

{markdown_doc}

그리고 아래는 고려 가능한 전략 목록입니다:

{formatted_strategy_list}

전략 목록에서 가장 적합하다고 판단되는 전략 3개를 선택하고, 각 전략을 선택한 이유도 함께 작성해주세요.
응답은 JSON 배열 형태로 아래와 같이 작성해주세요:

{example_response}
""")
    ])

    messages = prompt.format_messages()
    response = llm.invoke(messages)
    print("🧾 LLM 응답 원문 ↓↓↓")
    print(response.content)
    print("")
    return parse_llm_response(response.content)


def format_strategy_definitions(strategies: List[Dict]) -> str:
    return "\n".join([
        f"- {s['name']}: {s['description']} (사용 시점: {s['when_to_use']})"
        for s in strategies
    ])

def parse_llm_response(text: str) -> List[Dict]:
    import json
    import re

    # ```json ... ``` 블록 제거
    if "```json" in text:
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            text = match.group(1)

    try:
        return json.loads(text)
    except Exception as e:
        print("❗ 전략 선택 응답 파싱 오류:", e)
        return []