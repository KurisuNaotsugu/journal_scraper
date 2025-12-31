# db/repositories/search_result.py
from sqlalchemy.orm import selectinload
from db.models import (SearchResult, Keyword, Paper, PaperSummary)

SUMMARY_KEY_MAP = {
    "目的": "purpose",
    "対象": "sample",
    "方法": "method",
    "結果": "result",
    "結論": "conclusion",
}
def normalize_summary(summary: dict) -> dict:
    normalized = {}
    for k, v in summary.items():
        if k in SUMMARY_KEY_MAP:
            normalized[SUMMARY_KEY_MAP[k]] = v
    return normalized

class SearchResultRepository:

    def __init__(self, session):
        self.session = session

    def create(self, title, search_period, paper_count):
        obj = SearchResult(
            title=title,
            search_period=search_period,
            paper_count=paper_count,
        )
        self.session.add(obj)
        return obj

    def get(self, id_):
        return (
            self.session.query(SearchResult)
            .options(
                selectinload(SearchResult.keywords),
                selectinload(SearchResult.papers),
            )
            .get(id_)
        )

    def list_latest(self, limit=20):
        return (
            self.session.query(SearchResult)
            .order_by(SearchResult.id.desc())
            .limit(limit)
            .all()
        )

    def delete(self, id_):
        obj = self.get(id_)
        if obj:
            self.session.delete(obj)
        return obj

    def get_or_create_keyword(self, name: str) -> Keyword:
        keyword = (
            self.session.query(Keyword)
            .filter_by(name=name)
            .one_or_none()
        )
        if not keyword:
            keyword = Keyword(name=name)
            self.session.add(keyword)
        return keyword

    def create_search_result(
        self,
        title: str,
        search_period: str,
        keywords: list[str],
        papers: list[dict],
    ) -> SearchResult:

        # --- SearchResult ---
        result = SearchResult(
            title=title,
            search_period=search_period,
            paper_count=len(papers),
        )
        self.session.add(result)

        # --- keywords ---
        for kw in keywords:
            result.keywords.append(
                self.get_or_create_keyword(kw)
            )

        # --- papers ---
        for p in papers:
            paper = Paper(
                pmid=p["pmid"],
                title=p["title"],
                pubdate=p.get("pubdate"),
                url=p.get("url"),
                abstract=p.get("abstract"),
            )
            result.papers.append(paper)

            # --- summary ---
            summary = p.get("summary")
            if summary:
                if isinstance(summary, dict):
                    paper.summary = PaperSummary(
                        **normalize_summary(summary)
                    )
                else:
                    # 文字列だけ来た場合の保険
                    paper.summary = PaperSummary(
                        conclusion=str(summary)
                    )

        return result