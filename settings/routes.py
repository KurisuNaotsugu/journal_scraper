from flask import Blueprint, render_template, request, current_app, redirect, url_for, flash, abort
import json
from pathlib import Path

from . import settings_bp

@settings_bp.route("/keywords")
def keywords_page():
    settings_path = Path(current_app.root_path) / "settings" / "settings.json"

    # ファイルがなければ作成
    if not settings_path.exists():
        settings_path.write_text("[]", encoding="utf-8")
    # ファイルを読み込み
    with open(settings_path, "r", encoding="utf-8") as f:
        settings_list = json.load(f)

    return render_template("keywords_list.html", settings=settings_list)


@settings_bp.route("/keywords/new", methods=["GET", "POST"])
def keywords_new():
    settings_path = Path(current_app.root_path) / "settings" / "settings.json"
    settings_list = json.loads(settings_path.read_text(encoding="utf-8"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        raw = request.form.get("keywords", "")

        keywords = [k.strip() for k in raw.split("\n") if k.strip()]

        settings_list.append({
            "search_title": title,
            "keywords": keywords
        })

        settings_path.write_text(json.dumps(settings_list, ensure_ascii=False, indent=2), encoding="utf-8")
        flash("新しい設定を追加しました！", "success")
        return redirect(url_for("settings.keywords_page"))

    return render_template("keywords_edit.html", mode="new")

@settings_bp.route("/keywords/<int:i>/edit", methods=["GET", "POST"])
def keywords_edit(i):
    settings_path = Path(current_app.root_path) / "settings" / "settings.json"
    settings_list = json.loads(settings_path.read_text(encoding="utf-8"))

    if i < 0 or i >= len(settings_list):
        abort(404)

    item = settings_list[i]

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        raw = request.form.get("keywords", "")

        item["search_title"] = title
        item["keywords"] = [k.strip() for k in raw.split("\n") if k.strip()]

        settings_path.write_text(json.dumps(settings_list, ensure_ascii=False, indent=2), encoding="utf-8")
        flash("設定を更新しました！", "success")
        return redirect(url_for("settings.keywords_page"))

    return render_template("keywords_edit.html", mode="edit", item=item, index=i)

@settings_bp.route("/keywords/<int:i>/delete", methods=["POST"])
def keywords_delete(i):
    settings_path = Path(current_app.root_path) / "settings" / "settings.json"
    settings_list = json.loads(settings_path.read_text(encoding="utf-8"))

    if i < 0 or i >= len(settings_list):
        abort(404)

    settings_list.pop(i)

    settings_path.write_text(json.dumps(settings_list, ensure_ascii=False, indent=2), encoding="utf-8")
    flash("設定を削除しました。", "warning")

    return redirect(url_for("settings.keywords_page"))
