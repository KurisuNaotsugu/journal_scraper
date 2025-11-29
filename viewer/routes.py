from flask import Blueprint, render_template, url_for, current_app, request, abort
from pathlib import Path
import json
import re
from datetime import datetime

from . import viewer_bp

@viewer_bp.route('/')
def view_page():
    results_dir = Path(current_app.root_path) / "search_result"

    # --- ファイル一覧取得（YYYY-MM-DD-YYYY-MM-DD.json形式のみ） ---
    pattern = re.compile(r"(\d{4}-\d{2}-\d{2})-(\d{4}-\d{2}-\d{2})\.json$")
    json_files = []

    for f in results_dir.glob("*.json"):
        match = pattern.search(f.name)
        if match:
            start_date = match.group(1)
            end_date = match.group(2)
            json_files.append({
                "path": f,
                "name": f.name,
                "start_date": start_date,
                "end_date": end_date,
                "end_dt": datetime.strptime(end_date, "%Y-%m-%d")
            })

    if not json_files:
        return "No result files found.", 404

    # --- URL パラメータ file=xxx.json を取得 ---
    requested_file = request.args.get("file")

    if requested_file:
        # 指定ファイルが存在するかチェック
        matched = next((f for f in json_files if f["name"] == requested_file), None)
        if not matched:
            return abort(404, description="Requested file not found.")
        target_file = matched
    else:
        # file がない → 最新のファイルを使用
        target_file = max(json_files, key=lambda x: x["end_dt"])

    # --- JSON内容を読み込み ---
    try:
        with open(target_file["path"], "r", encoding="utf-8") as f:
            results = json.load(f)
    except Exception:
        return abort(500, description="Failed to read JSON file.")

    # --- テンプレートへ渡す ---
    return render_template(
        "view_results.html",
        results=results,
        archive_files=[f["name"] for f in json_files],
        current_file=target_file["name"]
    )