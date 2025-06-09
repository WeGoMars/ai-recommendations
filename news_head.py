# 뉴스 분석 프롬프트 정의
news_analysis_prompt = PromptTemplate(
    input_variables=["company_name", "news_data"],
    template="""

    {company_name}Ol] 대한 최신 FAS 분석해주세요.

    아래는 {company_name}O] 대한 최신 뉴스 목록입니다:

    {news_data}
뉴스들을 종합하여 (company_name}2| 최신 SAB 간략히 요약해주세요.
반드시 한국어(한글)로 답변해주세요.
"""
)

# 뉴스 분석 실행 부분

news_result = news_analysis_chain.invoke({
"company_name": company_name,
"news_data": json.dumps(news_data, ensure_ascii=False)

})

news_summary = news_result["text"]