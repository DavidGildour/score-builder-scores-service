import json


def get_json_content(response) -> dict:
    """ Returns a dict-translated JSON with content of the response """
    return json.loads(response.get_data(as_text=True))['content']


def test_getting_public_scores(client):
    resp = client.get('/scores')
    assert resp.status_code == 200

    data = get_json_content(resp)

    assert all(score['public'] for score in data), "Should only receive public scores"
    assert len(data) == 2, "Should be only two public scores"


def test_getting_user_scores(client):
    resp = client.get('/scores/test1') # test1 is a premade test user id
    assert resp.status_code == 200

    data = get_json_content(resp)

    assert all(score['user_id'] == 'test1' for score in data), "Should receive only user-specific scores"
    assert any(not score['public'] for score in data), "Should receive non-public scores as well"

    resp = client.get('/scores/null')
    assert resp.status_code == 200, "Should succeed even though there's no user with this ID"
    assert len(get_json_content(resp)) == 0, "But should provide no scores what-so-ever"


def test_adding_a_new_score(client):
    resp = client.post('/scores/test1', data=dict())
    assert resp.status_code == 400, "Should fail to add an improper score"

    resp = client.post('/scores/test1', data=dict(
        name="foo",
        public=True,
        score="{}"
    ))
    assert resp.status_code == 409, "Should fail to add a score with duplicate name"

    resp = client.post('/scores/test1', data=dict(
        name="foobar",
        public=True,
        score="{}"
    ))
    assert resp.status_code == 200, "Should successfully add a proper score"

    resp = client.get('/scores')
    assert len(get_json_content(resp)) == 3, "Should now receive three public scores"


def test_getting_single_score(client):
    resp = client.get('/scores/test1/foobar')
    assert resp.status_code == 200, "Should successfully retrieve a users score"
    assert get_json_content(resp)['name'] == 'foobar', "Score's name should match the queried one"

    resp = client.get('/scores/test1/barfoo')
    assert resp.status_code == 400, "Should fail to retrieve a non-existent one"


def test_modifying_score(client):
    resp = client.patch('/scores/test1/barfoo', data=dict(
        name="foofoo"
    ))
    assert resp.status_code == 400, "Should fail to modify non-existent score"

    resp = client.patch('/scores/test1/foobar', data=dict(
        name="foo"
    ))
    assert resp.status_code == 409, "Should fail to change the name to one already in use"

    resp = client.patch('/scores/test1/foobar', data=dict(
        public=False,
        name="barfoo"
    ))
    assert resp.status_code == 200, "Should successfully modify the existing score"
    assert get_json_content(resp)['name'] == 'barfoo', "Should modify the name column"
    assert not get_json_content(resp)['public'], "Should modify the public column."

    resp = client.get('/scores')
    assert len(get_json_content(resp)) == 2, "Should now receive two public scores again."


def test_deleting_score(client):
    resp = client.delete('/scores/test1/foobar')
    assert resp.status_code == 400, "Should fail to delete a non-existent score"

    resp = client.delete('/scores/test1/barfoo')
    assert resp.status_code == 200, "Should successfully delete a score"

    resp = client.get('/scores/test1')
    assert len(get_json_content(resp)) == 2, "This user should have only two scores again"
