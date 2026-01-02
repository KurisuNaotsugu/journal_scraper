from sqlalchemy import (Column, Integer, String, Text, ForeignKey, Table)
from sqlalchemy.orm import relationship
from db.database import Base

# -- Config Models --ーーーーーーーーーーーーーーーーーーーーーーー
class SearchConfig(Base):
    __tablename__ = "search_configs"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)  # 検索タイトル

    keywords = relationship(
        "KeywordConfig",
        secondary="search_config_keywords",
        back_populates="search_configs"
    )

class KeywordConfig(Base):
    """論文検索キーワード設定モデル
    """
    __tablename__ = "keyword_configs"

    id = Column(Integer, primary_key=True)
    keyword = Column(String, unique=True, nullable=False)
    enabled = Column(Integer, default=1)
    search_configs = relationship(
        "SearchConfig",
        secondary="search_config_keywords",
        back_populates="keywords"
    )

search_config_keywords = Table(
    "search_config_keywords",
    Base.metadata,
    Column("search_config_id", ForeignKey("search_configs.id"), primary_key=True,),
    Column("keyword_config_id",ForeignKey("keyword_configs.id"), primary_key=True,),
)

class AppState(Base):
    """
    アプリ内部状態管理モデル
    - last_search_date など、JSONで管理していた状態を保存
    """

    __tablename__ = "app_state"

    id = Column(Integer, primary_key=True)
    last_search_date = Column(String(20), nullable=False)


# -- Result Models --ーーーーーーーーーーーーーーーーーーーーーーー
class SearchResult(Base):
    __tablename__ = "search_results"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    search_period = Column(String(50))
    paper_count = Column(Integer)

    keywords = relationship(
        "Keyword",
        secondary="search_result_keywords",
        back_populates="search_results",
    )

    papers = relationship(
        "Paper",
        back_populates="search_result",
        cascade="all, delete-orphan",
    )

class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)

    search_results = relationship(
        "SearchResult",
        secondary="search_result_keywords",
        back_populates="keywords",
    )

search_result_keywords = Table(
    "search_result_keywords",
    Base.metadata,
    Column("search_result_id", ForeignKey("search_results.id"), primary_key=True),
    Column("keyword_id", ForeignKey("keywords.id"), primary_key=True),
)

class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True)
    pmid = Column(String(20), unique=True, nullable=False)
    title = Column(Text, nullable=False)
    pubdate = Column(String(50))
    url = Column(Text)
    abstract = Column(Text)

    search_result_id = Column(
        Integer, ForeignKey("search_results.id"), nullable=False
    )

    search_result = relationship(
        "SearchResult",
        back_populates="papers",
    )

    summary = relationship(
        "PaperSummary",
        uselist=False,
        back_populates="paper",
        cascade="all, delete-orphan",
    )

class PaperSummary(Base):
    __tablename__ = "paper_summaries"

    id = Column(Integer, primary_key=True)

    purpose = Column(Text)
    sample = Column(Text)
    method = Column(Text)
    result = Column(Text)
    conclusion = Column(Text)

    paper_id = Column(
        Integer, ForeignKey("papers.id"), unique=True, nullable=False
    )

    paper = relationship("Paper", back_populates="summary")
