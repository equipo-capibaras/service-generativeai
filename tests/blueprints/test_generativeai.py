import base64
import json
from typing import Any, cast
from unittest.mock import Mock, patch

from faker import Faker
from unittest_parametrize import ParametrizedTestCase, parametrize
from werkzeug.test import TestResponse

from app import create_app
from models import Role
from utils import mock_suggestions_dict


class TestIncidentsAISuggestions(ParametrizedTestCase):
    def setUp(self) -> None:
        self.faker = Faker()
        self.app = create_app()
        self.client = self.app.test_client()

    def gen_token_client(self, *, client_id: str | None, role: Role) -> dict[str, Any]:
        return {
            'sub': self.faker.uuid4(),
            'cid': client_id,
            'role': role.value,
            'aud': role.value,
        }

    def encode_token(self, token: dict[str, Any]) -> str:
        token_json = json.dumps(token).encode()
        return base64.urlsafe_b64encode(token_json).decode()

    def call_suggestions_api(self, incident_id: str, language: str, token: dict[str, Any] | None) -> TestResponse:
        token_encoded = None if token is None else self.encode_token(token)
        return self.client.get(
            f'/api/v1/incidents/{incident_id}/generativeai/suggestions',
            headers={} if token is None else {'X-Apigateway-Api-Userinfo': token_encoded},
            query_string={'locale': language},
        )

    @parametrize(
        'missing_field',
        [
            ('sub',),
            ('cid',),
            ('role',),
            ('aud',),
        ],
    )
    def test_info_token_missing_fields(self, missing_field: str) -> None:
        token = self.gen_token_client(
            client_id=cast(str, self.faker.uuid4()),
            role=cast(Role, self.faker.random_element(list(Role))),
        )
        del token[missing_field]

        incident_id = cast(str, self.faker.uuid4())

        resp = self.call_suggestions_api(incident_id, 'es-CO', token)

        self.assertEqual(resp.status_code, 401)
        resp_data = json.loads(resp.get_data())

        self.assertEqual(resp_data, {'code': 401, 'message': f'{missing_field} is missing in token'})

    def test_info_no_token(self) -> None:
        incident_id = cast(str, self.faker.uuid4())

        resp = self.call_suggestions_api(incident_id, 'es-CO', None)

        self.assertEqual(resp.status_code, 401)
        resp_data = json.loads(resp.get_data())

        self.assertEqual(resp_data, {'code': 401, 'message': 'Token is missing'})

    @parametrize(
        ('language',),
        [
            ('es-CO',),
            ('es-AR',),
            ('pt-BR',),
        ],
    )
    @patch('random.choice')
    def test_suggestions_pt_br(self, mock_choice: Mock, language: str) -> None:
        mock_choice.side_effect = lambda x: x[0]
        token = self.gen_token_client(client_id=str(self.faker.uuid4()), role=Role.AGENT)
        incident_id = str(self.faker.uuid4())

        response = self.call_suggestions_api(incident_id, language, token)

        self.assertEqual(response.status_code, 200)
        self.assertIn(response.json, mock_suggestions_dict[language])
