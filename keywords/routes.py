from flask import Blueprint, render_template, request
from .modules import fetch_weekly_counts
from . import keywords_bp  

@keywords_bp.route('/keywords')
def weekly_graph():
    labels = []
    values = []

    if request.method == 'POST':
        keywords_str = request.form.get('keywords', '')
        weeks = int(request.form.get('weeks', 8))  # デフォルト8週間

        keywords = [k.strip() for k in keywords_str.split() if k]

        if keywords:
            data = fetch_weekly_counts(keywords, weeks)
            labels = list(data.keys())
            values = list(data.values())

    return render_template('trend.html', labels=labels, values=values)