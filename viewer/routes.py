from flask import Blueprint, render_template, url_for, current_app
from pathlib import Path
import json

from . import view_bp

@view_bp.route('/view')
def view_page():
    json_path = Path(current_app.root_path) / "cli" / "result.json"
    
    if not json_path.exists():
        return "<h3>結果ファイルが存在しません。</h3>"

    with open(json_path, "r", encoding="utf-8") as f:
        results = json.load(f)


    return render_template("view_results.html", results=results)