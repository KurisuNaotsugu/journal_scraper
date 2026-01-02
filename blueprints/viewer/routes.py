from flask import render_template, url_for, abort, flash, redirect
from flask import current_app, request
from pathlib import Path
import json
import re
from datetime import datetime

from . import viewer_bp
from db.models import SearchResult
from db.database import SessionLocal
from db.repositories.search_result import SearchResultRepository

def build_results_dict(result):
    return {
        "title": result.title,
        "search_period": result.search_period,
        "paper_count": len(result.papers),  # ← これを追加
        "papers": [
            {
                "pmid": p.pmid,
                "title": p.title,
                "abstract": p.abstract,
                "summary": {
                    "purpose": p.summary.purpose if p.summary else None,
                    "method": p.summary.method if p.summary else None,
                    "result": p.summary.result if p.summary else None,
                    "conclusion": p.summary.conclusion if p.summary else None,
                },
            }
            for p in result.papers
        ]
    }

@viewer_bp.route('/')
def view_page():
    with SessionLocal() as session:
        repo = SearchResultRepository(session)
        archives = repo.find_all()

        if not archives:
            return "No search results found.", 404

        current = archives[0]
        results_dict = build_results_dict(current)

        print("\n===== DEBUG view_page =====")
        print(f"archives count: {len(archives)}")
        print("archives ids:", [a.id for a in archives])

        if not archives:
            print("No archives found")
            return "No search results found.", 404

        current = archives[0]
        print("\n--- current(SearchResult model) ---")
        print(current)

        results_dict = build_results_dict(current)

        print("\n--- results_dict (passed to template) ---")
        print(results_dict)
        print("===== END DEBUG =====\n")

    return render_template(
        "view_results.html",
        results=results_dict,   # ← 常に dict
        archives=archives,
        current_id=current.id,
    )


@viewer_bp.route("/<int:result_id>")
def view_archive(result_id):
    with SessionLocal() as session:
        repo = SearchResultRepository(session)
        result = repo.find_by_id(result_id)
        if not result:
            abort(404)

        archives = repo.find_all()
        results_dict = build_results_dict(result)

    return render_template(
        "view_results.html",
        results=results_dict,   # ← ここも dict
        archives=archives,
        current_id=result.id,
    )


@viewer_bp.route("/clear_archives", methods=["POST"])
def clear_archives():
    with SessionLocal() as session:
        session.query(SearchResult).delete()
        session.commit()

    flash("All search results deleted.", "warning")
    return redirect(url_for("viewer.view_page"))