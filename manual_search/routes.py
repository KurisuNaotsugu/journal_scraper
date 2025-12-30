from flask import render_template, request, jsonify
from cli.weekly_search import manual_search

from . import manualsearch_bp  

@manualsearch_bp.route("/", methods=["GET"])
def index():
    return render_template("manual_search.html")

@manualsearch_bp.route("/run", methods=["POST"])
def run():
    try:
        keywords_text = request.form.get("keywords")
        mindate = request.form.get("mindate")
        maxdate = request.form.get("maxdate")

        # キーワードを改行区切りで JSON 用の形式に変換
        keywords = [kw.strip() for kw in keywords_text.split("\n") if kw.strip()]
        input_json = [{"search_title": "Manual Search", "keywords": keywords}]

        # マニュアルサーチ実行
        results = manual_search(input_json, mindate, maxdate)

        return jsonify({"status": "success", "results": results})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})