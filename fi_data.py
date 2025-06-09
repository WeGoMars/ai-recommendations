# 재무 정보 수집 함수                                                                 객관적인 지표와 데이터를 중심으로 분석해주세요.

def fetch_financial_data(ticker):                
    """특정 종목의 상세 재무 정보를 가져옵니다."""

    try:
    # 한국 주식인 경우 'KS' 접미사 추가                                          
        if isinstance(ticker, str) and ticker.isdigit() and len(ticker) == 6:                                              1. 수익성 지표:
            ticker = f"{ticker}.ks"
        
        stock = yf.Ticker(ticker)

# 재무 분석 프롬프트 정의  

financial_analysis_prompt = PromptTemplate(
    input_variables=["company_name", "financial_data", "sentiment_result"],

    template="""
        {company_name}2|] 재무 정보와 뉴스 감성 분석 결과를 종합적으로 분석해주세요.    
        재무 정보: 
        {financial_data}
        뉴스 감성 분석 결과: 
        {sentiment_result}
        
         위 정보를 바탕으로 {company_name} 재무 상태와 투자 관점에서의 시사점을 객관적인 지표와 데이터를 중심으로 분석해주세요.
        다음 형식으로 한국어(한글)로 답변해주세요:

        ## 재무 지표 분석
        (제공된 데이터에 있는 지표만 분석해주세요)

1. 수익성 지표:
   순이익률: [수치]% (산업 평균: [수치]%)
 ROE: 자기자본수익률): [수치]% (산업 평균: [수치]%)


  2. 안정성 지표:

유동비율: [수치] (산업 평균: [수치])
부채비율: [수치]% (산업 Bat: [수치]%)

 3. 가치 지표:
(주가수익비율): [수치] 
 - 배당수익률: [수치]%

 
 4. 시장 지표:
- 시가총액: [수치] 원
- 52주 최고/최저 대비 현재가: 현재가가 최고가의 [수치]%, 최저가의 [수치]%


He 산업 내 위치
- 산업 내 재무 건전성 순위:[상위/중위/하위]

- 주요 경쟁사 대비 특징:[데이터 기반 분석]

\# 뉴스 및 감성 분석과의 연관성
- 최근 뉴스가 재무 상태에 미치는 영향:[객관적 분석]

- 뉴스 감성과 투자 관점의 연관성:[데이터 기반 분석]

## 투자 시사점

- 단기 관점 (3개월):[객관적 시사점]

- 중장기 관점 (6개월 이상):[객관적 시사점]

## 종합 평가
- 재무 건전성: [A+/A/B+/B/C+/C/D] (정량적 지표 기반)
- 투자 MAS: [상/중상/중/중하/하] (정량적 지표 기반)

의견은 배제하고, 오직 데이터와 객관적 지표에 근거하여 분석해주세요.
제공된 데이터에 없는 SSS SAMA 제외해주세요.
"""

)
# 재무 분석 실행 부분

financial_result = financial_analysis_chain.invoke({
"company_name": company_name,
"financial_data": json.dumps(financial_data, ensure_ascii=False),
"sentiment_result": sentiment_analysis

})

financial_analysis = financial_result["text"]
