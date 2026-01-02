# db/repositories/paper.py
from db.models import Paper

class PaperRepository:
    def __init__(self, session):
        self.session = session

    def create(self, **kwargs):
        paper = Paper(**kwargs)
        self.session.add(paper)
        return paper

    def find_by_id(self, paper_id: int):
        return (
            self.session.query(Paper)
            .filter_by(id=paper_id)
            .one_or_none()
        )

    def delete(self, paper):
        self.session.delete(paper)
