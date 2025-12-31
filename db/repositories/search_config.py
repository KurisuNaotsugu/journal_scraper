# db/repositories/search_config.py
from db.models import SearchConfig, KeywordConfig

class SearchConfigRepository:
    def __init__(self, session):
        self.session = session

    def create(self, title: str, keywords: list[str]):
        """
        新しい検索設定を作成
        keywords は文字列リスト
        """
        # キーワードオブジェクト取得 or 作成
        keyword_objs = []
        for kw in keywords:
            kw_obj = self.session.query(KeywordConfig).filter_by(keyword=kw).one_or_none()
            if not kw_obj:
                kw_obj = KeywordConfig(keyword=kw, enabled=1)
                self.session.add(kw_obj)
            keyword_objs.append(kw_obj)

        config = SearchConfig(title=title, keywords=keyword_objs)
        self.session.add(config)
        return config

    def find_all(self):
        return self.session.query(SearchConfig).order_by(SearchConfig.title).all()

    def find_by_title(self, title: str):
        return self.session.query(SearchConfig).filter_by(title=title).one_or_none()

    def find_by_id(self, cfg_id: int):
        return (
            self.session.query(SearchConfig)
            .filter(SearchConfig.id == cfg_id)
            .one_or_none()
        )
    
    def update_keywords(self, title: str, keywords: list[str]):
        config = self.find_by_title(title)
        if not config:
            return None
        # 新しいキーワードリストに更新
        keyword_objs = []
        for kw in keywords:
            kw_obj = self.session.query(KeywordConfig).filter_by(keyword=kw).one_or_none()
            if not kw_obj:
                kw_obj = KeywordConfig(keyword=kw, enabled=1)
                self.session.add(kw_obj)
            keyword_objs.append(kw_obj)
        config.keywords = keyword_objs
        return config

    def delete(self, cfg_id: int):
        config = self.find_by_id(cfg_id)
        if config:
            self.session.delete(config)
        return config
