# db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Base :ORMベースクラス
class Base(DeclarativeBase):
    pass


# Engine :DB接続設定
ENGINE = create_engine(
    "sqlite:///journal_scraper.db",
    future=True,
    echo=False,   # デバッグしたいなら True
)


# Session :DBセッション生成
SessionLocal = sessionmaker(
    bind=ENGINE,
    autoflush=False,
    autocommit=False,
)
