import random
from typing import Any

from flask import Blueprint, Response, current_app, request
from flask.views import MethodView

from utils import mock_suggestions_dict

from .util import class_route, json_response, requires_token

blp = Blueprint('Generative_AI', __name__)


@class_route(blp, '/api/v1/incidents/<incident_id>/generativeai/suggestions')
class IncidentsAISuggestions(MethodView):
    @requires_token
    def get(self, token: dict[str, Any], incident_id: str) -> Response:
        current_app.logger.debug('User %s requested suggestions for incident %s', token['sub'], incident_id)

        locale = request.args.get('locale', 'es-CO')

        suggestions_list = mock_suggestions_dict[locale]

        random_suggestion = random.choice(suggestions_list)  # noqa: S311

        return json_response(random_suggestion, 200)
