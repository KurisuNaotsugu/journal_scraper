from flask import Blueprint, render_template, request, current_app, redirect, url_for, flash
import json
from pathlib import Path

from . import settings_bp

@settings_bp.route("/keywords", methods=["GET", "POST"])
def keywords():
    settings_path = Path(current_app.root_path) / "settings" / "settings.json"

    # 設定ファイルが存在しない場合は生成
    if not settings_path.exists():
        settings_path.write_text(json.dumps({"keywords": []}, ensure_ascii=False, indent=2))

    # 現在の設定読み込み
    with open(settings_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    if request.method == "POST":
        # textarea から受け取る（1行1キーワード）
        raw = request.form.get("keywords", "")
        new_keywords = [
            kw.strip() for kw in raw.split("\n") if kw.strip()
        ]

        # 保存
        config["keywords"] = new_keywords

        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        flash("キーワードを更新しました！", "success")
        return redirect(url_for("settings.keywords_page"))

    return render_template("keywords_settings.html", config=config)
