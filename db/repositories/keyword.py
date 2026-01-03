# db/repositories/keyword.py
from db.models import Keyword
from sqlalchemy.exc import IntegrityError

class KeywordRepository:
    def __init__(self, session):
        self.session = session

    def get_or_create(self, name):
        obj = self.session.query(Keyword).filter_by(name=name).one_or_none()
        if obj:
            return obj

        obj = Keyword(name=name)
        self.session.add(obj)
        try:
            self.session.flush()
            return obj
        except IntegrityError:
            self.session.rollback()
            return (
                self.session.query(Keyword)
                .filter_by(name=name)
                .one()
            )

    def find_all(self):
        return self.session.query(Keyword).order_by(Keyword.name).all()
