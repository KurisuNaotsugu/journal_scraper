from flask import render_template, request, current_app, redirect, url_for, flash, abort
import json
from pathlib import Path

from . import settings_bp

# ヘルパー関数
def _settings_path() -> Path:
    return Path(current_app.root_path) / "settings" / "settings.json"

def load_settings() -> list:
    path = _settings_path()
    if not path.exists():
        path.write_text("[]", encoding="utf-8")
    return json.loads(path.read_text(encoding="utf-8"))

def save_settings(settings: list) -> None:
    path = _settings_path()
    path.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def get_item_or_404(settings: list, i: int) -> dict:
    if i < 0 or i >= len(settings):
        abort(404)
    return settings[i]

def delete_item(settings: list, i: int) -> None:
    get_item_or_404(settings, i)
    settings.pop(i)


# ルート関数
@settings_bp.route("/keywords")
def keywords_page():
    return render_template("keywords_list.html", settings=load_settings())


@settings_bp.route("/keywords/new", methods=["GET", "POST"])
def keywords_new():
    settings = load_settings()

    if request.method == "POST":
        settings.append({
            "search_title": request.form["title"].strip(),
            "keywords": [
                k.strip()
                for k in request.form["keywords"].splitlines()
                if k.strip()
            ]
        })
        save_settings(settings)
        flash("新しい設定を追加しました！", "success")
        return redirect(url_for("settings.keywords_page"))

    return render_template("keywords_edit.html", mode="new")

@settings_bp.route("/keywords/<int:i>/edit", methods=["GET", "POST"])
def keywords_edit(i):
    settings = load_settings()
    item = get_item_or_404(settings, i)

    if request.method == "POST":
        item["search_title"] = request.form.get("title", "").strip()
        item["keywords"] = [
            k.strip()
            for k in request.form.get("keywords", "").splitlines()
            if k.strip()
        ]

        save_settings(settings)
        flash("設定を更新しました！", "success")
        return redirect(url_for("settings.keywords_page"))

    return render_template(
        "keywords_edit.html",
        mode="edit",
        item=item,
        index=i
    )

@settings_bp.route("/keywords/<int:i>/delete", methods=["POST"])
def keywords_delete(i):
    settings = load_settings()
    delete_item(settings, i)

    save_settings(settings)
    flash("設定を削除しました。", "warning")
    return redirect(url_for("settings.keywords_page"))
