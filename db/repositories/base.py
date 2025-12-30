# db/repositories/base.py
class BaseRepository:
    def __init__(self, session):
        self.session = session

    def add(self, obj):
        self.session.add(obj)
        return obj

    def delete(self, obj):
        self.session.delete(obj)

    def get_by_id(self, model, id_):
        return self.session.get(model, id_)

    def list_all(self, model):
        return self.session.query(model).all()
