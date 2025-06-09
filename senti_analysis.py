
# 감성 분석 프롬프트 정의

sentiment_analysis_prompt = PromptTemplate(
input_variables=["company_name", "news_summary"],
template="""
다음은 {company_name} 관한 뉴스 요약입니다:
{news_summary}
위 내용의 감성(긍정/부정)을 분석하고, 주가에 미칠 SFB 평가해주세요.

다음 형식으로 한국어(한글)로 답변해주세요:

1. 전반적 감성: [긍정/부정/중립]
2. 감성 분석 근거:[뉴스에서 발견된 긍정적/부정적 요소]
3. 예상 주가 영향:[상승/하락/유지 전망과 그 이유]
"""
# 감성 분석 실행 부분
)
sentiment_result = sentiment_analysis_chain.invoke({
    "company_name": company_name,
    "news_summary": news_summary

})

sentiment_analysis = sentiment_result["text"]