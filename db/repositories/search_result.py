# db/repositories/search_result.py
from sqlalchemy.orm import selectinload
from db.models import SearchResult

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
