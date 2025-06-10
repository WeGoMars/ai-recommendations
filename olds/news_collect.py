import os

# final-stock-analyzerpyAlM| 뉴스 수집 함수

def fetch_stock_news(query):
    """네이버 검색 APIS 사용하여 주식 관련 최신 FAS 검색합니다."""
# 네이버 API 인증 정보
client_id = os.environ.get("NAVER_CLIENT_ID", "사용자 클라이언트 ID")

client_secret = os.environ.get("NAVER_CLIENT_SECRET", "사용자 클라이언트 Pw")

# 결과 저장 리스트
articles = []

try:
    print(f"naver API로 '{query}' 관련 뉴스를 검색 합니다...")

    