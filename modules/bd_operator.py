#db_operator.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 
from sqlalchemy.exc import IntegrityError
from extensions import db

""" 
# データ構造

SearchResult
 ├─ title
 ├─ keywords[]
 ├─ search_period
 ├─ paper_count
 └─ papers[]
        ├─ pmid
        ├─ title
        ├─ pubdate
        ├─ url
        ├─ abstract
        └─ summary {目的, サンプル, 解析手法, 結果, 結論}
"""


class SearchResult(db.Model):
    """検索結果モデル

    Attributes:
        id (int): 主キー (自動振り分け)
        title (str): 検索タイトル
        search_period (str): 検索期間
        paper_count (int): 今回の検索でヒットした論文数
        papers (list of Paper): Pubmedから取得した論文情報 (Paperオブジェクトのリスト)
        keywords (list of Keyword): 論文検索に使用したキーワード
    """
    __tablename__ = "search_results"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    search_period = db.Column(db.String(50))
    paper_count = db.Column(db.Integer)
    keywords = db.relationship("Keyword", secondary="search_result_keywords", back_populates="search_results")
    papers = db.relationship("Paper", backref="search_result", lazy=True)

class Keyword(db.Model):
    """検索キーワードモデル

    Attributes:
        id (int): 主キー (自動振り分け)
        name (str): キーワード
        search_results (list of SearchResult): このキーワードが関連する検索結果 (SearchResultオブジェクトのリスト)
    """
    __tablename__ = "keywords"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    search_results = db.relationship("SearchResult", secondary="search_result_keywords", back_populates="keywords")

# 中間テーブル: 検索結果とキーワードの多対多関係
search_result_keywords = db.Table(
    "search_result_keywords",
    db.Column("search_result_id", db.Integer, db.ForeignKey("search_results.id")),
    db.Column("keyword_id", db.Integer, db.ForeignKey("keywords.id"))
)

# 論文モデル
class Paper(db.Model):
    """論文メタデータモデル

    Attributes:
        id (int): 主キー (自動振り分け)
        pmid (str): PubMed ID
        title (str): 論文タイトル
        pubdate (str): 出版日
        url (str): 論文URL
        abstract (str): 論文要旨(英語)
        search_result_id (int): 関連する検索結果のID (外部キー)
        summary (PaperSummary): 論文要約情報 (PaperSummaryオブジェクト)
    """
    __tablename__ = "papers"

    id = db.Column(db.Integer, primary_key=True)
    pmid = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.Text, nullable=False)
    pubdate = db.Column(db.String(50))
    url = db.Column(db.Text)
    abstract = db.Column(db.Text)

    search_result_id = db.Column(db.Integer, db.ForeignKey("search_results.id"), nullable=False)
    summary = db.relationship("PaperSummary", uselist=False, backref="paper", cascade="all, delete")


class PaperSummary(db.Model):
    """アブストラクト要約モデル

    Attributes:
        id (int): 主キー (自動振り分け)
        purpose (str): 目的
        sample (str): サンプル
        method (str): 解析手法
        result (str): 結果
        conclusion (str): 結論
        paper_id (int): 関連する論文のID (外部キー)
    """
    __tablename__ = "paper_summaries"

    id = db.Column(db.Integer, primary_key=True)

    purpose = db.Column(db.Text)
    sample = db.Column(db.Text)
    method = db.Column(db.Text)
    result = db.Column(db.Text)
    conclusion = db.Column(db.Text)

    paper_id = db.Column(db.Integer,db.ForeignKey("papers.id"), unique=True, nullable=False)

def import_json(data):
    """JSONにまとめたデータをDBに挿入する（pmid重複対応版）"""

    for block in data:
        # search result
        search = SearchResult(
            title=block["title"],
            search_period=block["search_period"],
            paper_count=block["paper_count"]
        )
        db.session.add(search)

        # keywords（多対多）
        for kw in block["keywords"]:
            keyword = Keyword.query.filter_by(name=kw).first()
            if not keyword:
                keyword = Keyword(name=kw)
                db.session.add(keyword)
            search.keywords.append(keyword)

        # papers
        for p in block["papers"]:
            # 既存論文チェック（pmid）
            paper = Paper.query.filter_by(pmid=p["pmid"]).first()

            if not paper:
                # 新規論文
                paper = Paper(
                    pmid=p["pmid"],
                    title=p["title"],
                    pubdate=p["pubdate"],
                    url=p["url"],
                    abstract=p["abstract"],
                )

                # summary
                s = p.get("summary", {})
                summary = PaperSummary(
                    purpose=s.get("目的"),
                    sample=s.get("サンプル"),
                    method=s.get("解析手法"),
                    result=s.get("結果"),
                    conclusion=s.get("結論"),
                )
                paper.summary = summary
                db.session.add(paper)

            paper.search_result = search

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise


