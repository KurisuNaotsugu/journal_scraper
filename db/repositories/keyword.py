# db/repositories/keyword.py
from db.models import Keyword

class KeywordRepository:
    def __init__(self, session):
        self.session = session

    def get_or_create(self, name):
        obj = (
            self.session.query(Keyword)
            .filter_by(name=name)
            .one_or_none()
        )
        if not obj:
            obj = Keyword(name=name)
            self.session.add(obj)
        return obj

    def find_all(self):
        return self.session.query(Keyword).order_by(Keyword.name).all()
