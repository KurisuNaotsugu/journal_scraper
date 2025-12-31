from flask import render_template, request, current_app, redirect, url_for, flash, abort
from . import settings_bp
from db.database import SessionLocal
from db.repositories.search_config import SearchConfigRepository
from db.repositories.keyword_config import KeywordConfigRepository

# --- ヘルパー ---
def get_item_or_404(items, i):
    if i < 0 or i >= len(items):
        abort(404)
    return items[i]

# --- ルート ---
@settings_bp.route("/keywords")
def keywords_page():
    with SessionLocal() as session:
        search_repo = SearchConfigRepository(session)
        search_configs = search_repo.find_all()

        # JSONと同じ形式に整形
        data = []
        for sc in search_configs:
            data.append({
                "id": sc.id,
                "search_title": sc.title,
                "keywords": [kw.keyword for kw in sc.keywords]
            })

    return render_template("keywords_list.html", settings=data)

@settings_bp.route("/keywords/new", methods=["GET", "POST"])
def keywords_new():
    if request.method == "POST":
        title = request.form["title"].strip()
        keywords = [k.strip() for k in request.form["keywords"].splitlines() if k.strip()]

        with SessionLocal() as session:
            search_repo = SearchConfigRepository(session)
            search_cfg = search_repo.create(title=title, keywords=keywords)
            session.commit()

        flash("新しい設定を追加しました！", "success")
        return redirect(url_for("settings.keywords_page"))

    return render_template("keywords_edit.html", mode="new")

@settings_bp.route("/keywords/<int:cfg_id>/edit", methods=["GET", "POST"])
def keywords_edit(cfg_id):
    with SessionLocal() as session:
        search_repo = SearchConfigRepository(session)
        search_cfg = search_repo.find_by_id(cfg_id)
        if not search_cfg:
            abort(404)

        if request.method == "POST":
            title = request.form.get("title", "").strip()
            keywords = [k.strip() for k in request.form.get("keywords", "").splitlines() if k.strip()]

            search_repo.update_keywords(title=title, keywords=keywords)
            session.commit()

            flash("設定を更新しました！", "success")
            return redirect(url_for("settings.keywords_page"))

        item = {
            "id": search_cfg.id,
            "search_title": search_cfg.title,
            "keywords": [kw.keyword for kw in search_cfg.keywords]
        }
        return render_template("keywords_edit.html", mode="edit", item=item, index=cfg_id)

@settings_bp.route("/keywords/<int:cfg_id>/delete", methods=["POST"])
def keywords_delete(cfg_id):
    with SessionLocal() as session:
        search_repo = SearchConfigRepository(session)
        search_repo.delete(cfg_id)
        session.commit()
        flash("設定を削除しました。", "warning")
    return redirect(url_for("settings.keywords_page"))
