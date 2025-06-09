
# LangChain 관련 라이브러리 임포트
from langchain_openai import ChatOpenAl
from langchain.chains import LLMChain

from langchain.prompts import PromptTemplate

#UM 모델 설정

llm = ChatOpenAl(temperature=0.1, model="gpt-4")

# 프롬프트 템플릿 정의 및 체인 생성

news_analysis_chain = LLMChain(
IIm=llm,

prompt=news_analysis_prompt,

verbose=False
)


# 뉴스 분석 프롬프트 템플릿

ews_analysis_prompt = PromptTemplate(

input_variables=["company_name", "news_data"],


template="""

{company_name}Ol] 대한 최신 FAS 분석해주세요.

아래는 {company_name}O] 대한 최신 뉴스 목록입니다:

{news_data}

위 FASS 종합하여 {company_name}2| 최신 SAB 간략히 요약해주세요.

반드시 한국어(한글)로 답변해주세요.
"""
)



# 체인 생성

news_analysis_chain = LLMChain(
    llm=llm,
    prompt=news_analysis_prompt,
    verbose=False   
)

sentiment_analysis_chain = LLMChain(
    IIm=llm,
    prompt=sentiment_analysis_prompt,  
    verbose=False
)

financial_analysis_chain = LLMChain(

    IIm=llm,

    prompt=financial_analysis_prompt,

    verbose=False
)

# 1. 데이터 수집

news_data = fetch_stock_news(company_name)
financial_data = fetch_financial_data(ticker)

# 2. 뉴스 요약

news_result = news_analysis_chain.invoke({
    "company_name": company_name,
     "news_data": json.dumps(news_data, ensure_ascii=False)
})

news_summary = news_result["text"]

# 3. 감성 분석

sentiment_result = sentiment_analysis_chain.invoke({
"company_name": company_name,
"news_summary": news_summary
})
sentiment_analysis = sentiment_result["text"]



# 4. 재무 분석

financial_result = financial_analysis_chain.invoke({
    "company_name": company_name,
    "financial_data": json.dumps(financial_data, ensure_ascii=False),
    "sentiment_result": sentiment_analysis
})
financial_analysis = financial_result["text"]


#5. 결과 통합

result = {
    "ticker": ticker,
    "company_name": company_name,
    "news_titles": news_titles,
    "news_summary": news_summary,
    "sentiment_analysis": sentiment_analysis,
    "financial_analysis": financial_analysis,
    "raw_data": json_serializable({
    "news_data": news_data,
    "financial_data": financial_data
    }),
    "status": "success"
}