# db/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Base : ORMベースクラス
class Base(DeclarativeBase):
    pass


def get_database_url():
    """
    Render の DATABASE_URL を SQLAlchemy 用に補正して返す
    """
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        # ローカル開発用（SQLite）
        return "sqlite:///journal_scraper.db"

    # Render は postgres:// になることがあるため修正
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://", "postgresql://", 1
        )

    return database_url


# Engine : DB接続設定
ENGINE = create_engine(
    get_database_url(),
    future=True,
    echo=False,
    pool_pre_ping=True,  # Render対策（接続切れ防止）
)

# Session : DBセッション生成
SessionLocal = sessionmaker(
    bind=ENGINE,
    autoflush=False,
    autocommit=False,
)
