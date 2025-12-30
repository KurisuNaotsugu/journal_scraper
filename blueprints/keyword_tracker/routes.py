from flask import Blueprint, render_template, request
from modules.pubmed_operator import fetch_weekly_counts
from . import ktracker_bp  

@ktracker_bp.route('/weekly_graph', methods=['GET', 'POST'])
def weekly_graph():
    labels = []
    values = []
    keywords_str = "" 
    weeks = 8 

    if request.method == 'POST':
        keywords_str = request.form.get('keywords', '')
        weeks = int(request.form.get('weeks', 8))

        #print(f"Received keywords: {keywords_str}, weeks: {weeks}")

        keywords = [k.strip() for k in keywords_str.split() if k]

        if keywords:
            data = fetch_weekly_counts(keywords, weeks)
            labels = list(data.keys())
            values = list(data.values())

    return render_template(
        'keywords.html', 
        labels=labels,
        values=values, 
        keywords_str=keywords_str,
        weeks=weeks
        )