from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import os

# 환경 변수로부터 MySQL 연결 정보 설정
DB_HOST = os.getenv("DB_HOST", "13.220.145.152")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USERNAME = os.getenv("DB_USERNAME", "marsman")
DB_PASSWORD = os.getenv("DB_PASSWORD", "marsword")
DB_DATABASE = os.getenv("DB_DATABASE", "mars")

# MySQL 연결 문자열
DATABASE_URL = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

# SQLAlchemy Engine & Session 설정
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
