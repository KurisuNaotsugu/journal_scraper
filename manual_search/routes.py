from flask import Blueprint, render_template, request, jsonify
from modules.pubmed_operator import fetch_weekly_counts
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

        input_json = [{
            "search_title": "Manual Search",
            "keywords": keywords
        }]

        results = manual_search(input_json, mindate, maxdate)
        #print(results)
        return jsonify({"status": "success", "results": results})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})