# db/repositories/keyword_config.py
from db.models import KeywordConfig

class KeywordConfigRepository:
    def __init__(self, session):
        self.session = session

    def create(self, keyword, enabled=1):
        obj = KeywordConfig(keyword=keyword, enabled=enabled)
        self.session.add(obj)
        return obj

    def find_all(self):
        return self.session.query(KeywordConfig).order_by(KeywordConfig.keyword).all()

    def find_by_keyword(self, keyword):
        return (
            self.session.query(KeywordConfig)
            .filter_by(keyword=keyword)
            .one_or_none()
        )

    def update_enabled(self, keyword, enabled):
        obj = self.find_by_keyword(keyword)
        if obj:
            obj.enabled = enabled
        return obj

    def delete(self, keyword):
        obj = self.find_by_keyword(keyword)
        if obj:
            self.session.delete(obj)
        return obj
