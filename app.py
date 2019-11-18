from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from resources.score import UserScores, PublicScores, Score

app = Flask(__name__)
cors = CORS(app, supports_credentials=True, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])

api = Api(app)

api.add_resource(UserScores, '/scores/<string:user_id>')
api.add_resource(Score, '/scores/<string:user_id>/<string:score_name>')
api.add_resource(PublicScores, '/scores')