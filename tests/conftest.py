import pytest

from app import app
from db import db

from models.score import ScoreModel


@pytest.fixture(scope='module')
def client():
    """ Testing client for the scores service """
    app.config.from_object('config.TestingConfig')
    app.app_context().push()
    db.init_app(app)

    client = app.test_client()
    db.create_all()

    ScoreModel('foo', 'test1', {'notes': []}, True).save_to_db()
    ScoreModel('bar', 'test1', {'notes': []}, False).save_to_db()
    ScoreModel('foo', 'test2', {'notes': []}, False).save_to_db()
    ScoreModel('bar', 'test2', {'notes': []}, True).save_to_db()

    yield client

    db.session.close()
    db.drop_all()