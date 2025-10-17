from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base import Base


# DB 엔진 생성
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)

# 세션팩토리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 의존성 주입용 (FastAPI DI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
