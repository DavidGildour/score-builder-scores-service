from datetime import datetime

from db import db


class ScoreModel(db.Model):
    __tablename__ = 'scores'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(256), default="Created with Score Builder.")
    notes = db.Column(db.JSON, nullable=False)
    creation_date = db.Column(db.DateTime)
    last_edit  = db.Column(db.DateTime)
    public = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.String(22), nullable=False)

    def __init__(self, name, user_id, notes, public = False, description = None):
        self.name = name
        self.user_id = user_id
        self.notes = notes
        self.creation_date = datetime.now()
        self.last_edit = datetime.now()
        if description: self.description = description
        if public: self.public = public

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def json(self):
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description,
            'user_id': self.user_id,
            'created': str(self.creation_date)[:19],
            'last_edit': str(self.last_edit)[:19],
            'public': self.public,
            'data': self.notes,
        }

    @classmethod
    def find_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def find_by_name(cls, user_id, name):
        return cls.query.filter_by(user_id=user_id).filter_by(name=name).first()

    @classmethod
    def find_all_public(cls):
        return cls.query.filter_by(public=True).all()

    @classmethod
    def get_latest(cls, user_id):
        return cls.query.filter_by(user_id=user_id).order_by(ScoreModel.last_edit.desc()).first()
