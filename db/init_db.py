# cli/init_db.py
from database import ENGINE, SessionLocal, Base
from models import AppState, KeywordConfig, SearchConfig

def main(init_date:str):
    """データベースの初期化と初期データ挿入

    Args:
        init_date (str): 自動検索開始日 (YYYY-MM-DD)
    """
    Base.metadata.create_all(bind=ENGINE)
    print("DB tables ensured.")

    # -------------------------
    # ② 初期データ投入
    # -------------------------
    session = SessionLocal()
    try:
        # --- AppState 初期値 ---
        if session.query(AppState).first() is None:
            state = AppState(last_search_date=init_date)
            session.add(state)

        # --- SearchConfig 初期値 ---
        default_searches = [
            {
                "title": "Cancer treatment review",
                "keywords": ["cancer", "immunotherapy", "clinical trial", "chemotherapy", "radiation therapy"]
            }
        ]

        for s in default_searches:
            # SearchConfig 作成
            search_cfg = SearchConfig(title=s["title"])
            session.add(search_cfg)
            session.flush()

            # KeywordConfig と紐付け
            for kw_name in s["keywords"]:
                kw = session.query(KeywordConfig).filter_by(keyword=kw_name).first()
                if kw is None:
                    kw = KeywordConfig(keyword=kw_name, enabled=1)
                    session.add(kw)
                    session.flush()
                search_cfg.keywords.append(kw)

        # --- コミット ---
        session.commit()
        print("Initial data committed.")

    finally:
        session.close()

if __name__ == "__main__":
    main()
