# db/repositories/paper_summary.py
from db.models import PaperSummary

class PaperSummaryRepository:
    def __init__(self, session):
        self.session = session

    def create_or_update(self, paper, **summary_data):
        if paper.summary:
            for k, v in summary_data.items():
                setattr(paper.summary, k, v)
            return paper.summary

        summary = PaperSummary(**summary_data)
        paper.summary = summary
        self.session.add(summary)
        return summary
