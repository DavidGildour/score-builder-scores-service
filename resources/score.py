import datetime
import json

from flask_restful import Resource, reqparse

from models.score import ScoreModel


def json_type(data) -> dict:
    """ This method is here only because flask's test-client does not allow nested dictionaries inside a request body"""
    if isinstance(data, dict): return data
    return json.loads(data)


def bool_type(data) -> bool:
    """
    This method is here only because flask's test-client
    fucks up request bodies and does not preserve their intended types
    """
    if isinstance(data, bool): return data
    return False if data == "False" else True


class UserScores(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', required=True)
    parser.add_argument('public', type=bool, required=True)
    parser.add_argument('score', type=json_type, required=True)
    parser.add_argument('description')


    @classmethod
    def get(cls, user_id):
        return {
            'message': 'success',
            'content': [score.json() for score in ScoreModel.find_by_user_id(user_id)]
        }

    @classmethod
    def post(cls, user_id):
        data = cls.parser.parse_args()

        names = (score.name for score in ScoreModel.find_by_user_id(user_id))

        if data['name'] not in names:
            new_score = ScoreModel(data['name'], user_id, data['score'], public=data['public'], description=data['description'])
            new_score.save_to_db()

            return {
                'message': 'Successfully added new score.',
                'content': new_score.json()
            }
        return {
            'message': f'Name \"{data["name"]}\" was already used, try different name.',
        }, 409


class PublicScores(Resource):
    @classmethod
    def get(cls):
        return {
            'message': 'success',
            'content': [score.json() for score in ScoreModel.find_all_public()]
        }


class Score(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name')
    parser.add_argument('description')
    parser.add_argument('public', type=bool_type)
    parser.add_argument('notes', type=dict, help="Provided value is not JSON-like dictionary.")

    @staticmethod
    def fail_response(score):
        return {
            'message': f'Score {score} does not exist for this user',
        }, 400

    @classmethod
    def get(cls, user_id, score_name):
        score = ScoreModel.find_by_name(user_id, score_name)

        if score:
            return {
                'message': 'success',
                'content': score.json()
            }
        return cls.fail_response(score_name)

    @classmethod
    def patch(cls, user_id, score_name):
        data = cls.parser.parse_args()

        names = (score.name for score in ScoreModel.find_by_user_id(user_id))

        if data['name'] in names:
            return {
                'message': 'This name is already used. Try a different one.'
            }, 409
        
        score = ScoreModel.find_by_name(user_id, score_name)

        if score:
            for key, val in data.items():
                if val is not None:
                    setattr(score, key, val)

            score.last_edit = datetime.datetime.now()
            score.save_to_db()
            return {
                'message': f'Successfully updated score {score_name}.',
                'content': score.json(),
            }
        return cls.fail_response(score_name)

    @classmethod
    def delete(cls, user_id, score_name):
        score = ScoreModel.find_by_name(user_id, score_name)

        if score:
            score.remove_from_db()

            return {
                'message': f'Successfully removed score {score_name} from the database.'
            }
        return cls.fail_response(score_name)


class LatestScore(Resource):
    @classmethod
    def get(cls, user_id):
        score = ScoreModel.get_latest(user_id)

        if score:
            return {
                "message": "Successfully retrieved the latest score",
                'content': score.json()
            }
        return {
            "message": "No scores available for this user."
        }, 404