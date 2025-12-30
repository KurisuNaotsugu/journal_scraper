# db/repositories/paper.py
from db.models import Paper

class PaperRepository:
    def __init__(self, session):
        self.session = session

    def create(self, **kwargs):
        paper = Paper(**kwargs)
        self.session.add(paper)
        return paper

    def find_by_pmid(self, pmid):
        return (
            self.session.query(Paper)
            .filter_by(pmid=pmid)
            .one_or_none()
        )

    def delete(self, paper):
        self.session.delete(paper)
