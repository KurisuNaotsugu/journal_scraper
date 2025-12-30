# cli/init_db.py
from database import ENGINE, SessionLocal, Base
from models import AppState, KeywordConfig

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
        # AppState 初期値
        if session.query(AppState).first() is None:
            state = AppState(last_search_date="2025/01/01")
            session.add(state)

        # KeywordConfig 初期値（例）
        default_keywords = ["cancer", "diabetes", "Alzheimer"]
        for kw in default_keywords:
            if session.query(KeywordConfig).filter_by(keyword=kw).first() is None:
                session.add(KeywordConfig(keyword=kw, enabled=1))

        session.commit()  # ← DBに反映
        print("Initial data committed.")
    finally:
        session.close()

if __name__ == "__main__":
    main()
