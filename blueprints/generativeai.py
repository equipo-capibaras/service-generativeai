import random
from typing import Any

from flask import Blueprint, Response, request
from flask.views import MethodView

from models import Role
from utils import mock_suggestions_dict

from .util import class_route, error_response, json_response, requires_token

blp = Blueprint('Generative_AI', __name__)


@class_route(blp, '/api/v1/incidents/<incident_id>/generativeai/suggestions')
class IncidentsAISuggestions(MethodView):
    @requires_token
    def get(self, token: dict[str, Any], incident_id: str) -> Response:
        if incident_id is None:
            return error_response('Bad Request: The incident ID must be provided', 400)

        if token['role'] != Role.AGENT.value or token['cid'] is None:
            return error_response('Forbidden: You do not have access to this resource or must be linked to a company.', 403)

        locale = request.args.get('locale', 'es-CO')

        suggestions_list = mock_suggestions_dict[locale]

        random_suggestion = random.choice(suggestions_list)  # noqa: S311

        return json_response(random_suggestion, 200)
