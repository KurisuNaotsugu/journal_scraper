# cli/init_db.py
from database import ENGINE, SessionLocal, Base
from models import AppState, KeywordConfig, SearchConfig

def main():
    # -------------------------
    # ① テーブル作成（存在しなければ作る）
    # -------------------------
    Base.metadata.create_all(bind=ENGINE)
    print("DB tables ensured.")

    # -------------------------
    # ② 初期データ投入
    # -------------------------
    session = SessionLocal()
    try:
        # --- AppState 初期値 ---
        if session.query(AppState).first() is None:
            state = AppState(last_search_date="2025/01/01")
            session.add(state)

        # --- KeywordConfig 初期値 ---
        default_keywords = ["cancer", "diabetes", "Alzheimer"]
        for kw in default_keywords:
            if session.query(KeywordConfig).filter_by(keyword=kw).first() is None:
                session.add(KeywordConfig(keyword=kw, enabled=1))

        # --- SearchConfig 初期値 ---
        # 例: 検索タイトルごとに紐づくキーワードを作成
        default_searches = [
            {
                "title": "RCC biomarker discover",
                "keywords": ["RCC", "biomarker", "proteome", "human"]
            },
            {
                "title": "Cancer treatment review",
                "keywords": ["cancer", "immunotherapy", "clinical trial"]
            }
        ]

        for s in default_searches:
            # 既に存在するか確認
            if session.query(SearchConfig).filter_by(title=s["title"]).first() is None:
                # SearchConfig 作成
                search_cfg = SearchConfig(title=s["title"])
                session.add(search_cfg)
                session.flush()  # idを取得するためにflush

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
