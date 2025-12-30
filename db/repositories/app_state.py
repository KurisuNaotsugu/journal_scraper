# db/repositories/app_state.py
from db.models import AppState

class AppStateRepository:
    def __init__(self, session):
        self.session = session

    def get(self):
        return self.session.query(AppState).first()

    def get_or_create(self):
        state = self.get()
        if not state:
            state = AppState(last_search_date="2025/12/01")
            self.session.add(state)
        return state

    def update_last_search_date(self, date_str):
        state = self.get_or_create()
        state.last_search_date = date_str
        return state

    def delete(self):
        state = self.get()
        if state:
            self.session.delete(state)
        return state
