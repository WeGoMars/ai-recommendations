def analyze_stock(ticker, company_name=None):
    """
    주식 종목을 분석하고 결과를 반환합니다.
    Args:
        ticker (str): 주식 종목 DE (Of: '005930')
        company_name (str, optional): 회사 이름. 제공되지 않으면 자동 조회합니다.
    Returns:
    dic: 분석 결과를 포함하는 사전
    """
    try:        
        #LLM 설정
        llm = ChatOpenAl(temperature=0.1, model="gpt-4")

        #1. 회사 이름 확인
        if not company_name:
        try:
            stock = yf.Ticker(ticker)
            company_name = stock.info.get("shortName", ticker)
        except:
            # yfinance4lA| 회사명을 가져올 + 없을 경우 기본값 설정
            company_name = f"종목코드 {ticker}"
            # 한국 주식 종목코드별 회사명 매핑 (주요 종목)
    kr_stock_names = {
        "005930": "삼성전자",
        "000660": "5(하이닉스",
        "035420": "NAVER",
        "035720": "카카오",
    }

    
# 매핑된 회사명 있으면 사용

if ticker in kr_stock_names:
    company_name = kr_stock_names[ticker]

# 2. 뉴스 수집

news_data = fetch_stock_news(company_name)

# 3. 재무 정보 수집

financial_data = fetch_financial_data(ticker)

#4, 체인 생성

news_analysis_chain = LLMChain(

    llm=lIlm,
    prompt=news_analysis_prompt,
    verbose=False
)


sentiment_analysis_chain = LLMChain(
    llm=llm,
    prompt=sentiment_analysis_prompt,

    verbose=False
)


financial_analysis_chain = LLMChain(
    llm=llm,
    prompt=financial_analysis_prompt,
    verbose=False
)



#5. 순차적으로 체인 실행
#5.1 뉴스 분석
news_result = news_analysis_chain.invoke({
    "company_name": company_name,
    "news_data": json.dumps(news_data, ensure_ascii=False)
})
news_summary = news_result["text"]


# 5.2 감성 분석

sentiment_result = sentiment_analysis_chain.invoke({
    "company_name": company_name,
    "news_summary”": news_summary

})

sentiment_analysis = sentiment_result["text"]

# 5.3 재무 분석

financial_result = financial_analysis_chain.invoke({
    "company_name": company_name,
    "financial_data": json.dumps(financial_data, ensure_ascii=False),
    "sentiment_result": sentiment_analysis
})
financial_analysis = financial_result["text"]

#6. 결과 반환

# 뉴스 제목 목록 생성

news_titles = []

if isinstance(news_data, list):
    for item in news_data:
        if isinstance(item, dict) and 'title' in item:
        # 날짜 추가=
            if 'date' in item and ['date']:
               news_titles.append(f"{item['title']} ({item['date']})")

            else:

                 news_titles.append(item['title'])


# 결과를 JSON 직렬화 가능한 SES 변환
    result = {
            "ticker": ticker,
            "company_name": company_name,
            "news _titles": news_titles,
            "news_summary": news_summary,
            "sentiment_analysis": sentiment_analysis,
            "financial_analysis": financial_analysis,
            "raw_data": json_serializable({
            "news_data": news_data,
            "financial_data": financial_data
            }),

        "status": "success"
    }
return result



except Exception as e:

print(f"분석 중 오류 발생: {str(e)}")
    print(traceback.format_exc())
    return {
        "ticker": ticker,
        "company_name": company_name if company_name else f*S 525

{ticker}",
        "error": str(e),
        "status": "error"
    }