import base64
import json
from typing import Any
from unittest.mock import Mock, patch

from faker import Faker
from unittest_parametrize import ParametrizedTestCase

from app import create_app
from models import Role
from utils import suggestions, suggestions_es_ar, suggestions_pt_br


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

    @patch('random.choice')
    def test_access_denied(self, mock_choice: Mock) -> None:
        mock_choice.side_effect = lambda x: x[0]
        token = self.gen_token_client(client_id=None, role=Role.USER)
        token_encoded = self.encode_token(token)

        response = self.client.get(
            '/api/v1/incidents/generativeai/suggestions',
            headers={'X-Apigateway-Api-Userinfo': token_encoded},
        )

        self.assertEqual(response.status_code, 403)
        if response.json is not None:
            self.assertIn('Forbidden', response.json['message'])

    @patch('random.choice')
    def test_suggestions_pt_br(self, mock_choice: Mock) -> None:
        mock_choice.side_effect = lambda x: x[0]
        token = self.gen_token_client(client_id=str(self.faker.uuid4()), role=Role.AGENT)
        token_encoded = self.encode_token(token)

        response = self.client.get(
            '/api/v1/incidents/generativeai/suggestions',
            headers={'X-Apigateway-Api-Userinfo': token_encoded},
            query_string={'locale': 'pt-BR'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(response.json, suggestions_pt_br)

    @patch('random.choice')
    def test_suggestions_es_ar(self, mock_choice: Mock) -> None:
        mock_choice.side_effect = lambda x: x[0]
        token = self.gen_token_client(client_id=str(self.faker.uuid4()), role=Role.AGENT)
        token_encoded = self.encode_token(token)

        response = self.client.get(
            '/api/v1/incidents/generativeai/suggestions',
            headers={'X-Apigateway-Api-Userinfo': token_encoded},
            query_string={'locale': 'es-AR'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(response.json, suggestions_es_ar)

    @patch('random.choice')
    def test_default_suggestions(self, mock_choice: Mock) -> None:
        mock_choice.side_effect = lambda x: x[0]
        token = self.gen_token_client(client_id=str(self.faker.uuid4()), role=Role.AGENT)
        token_encoded = self.encode_token(token)

        response = self.client.get(
            '/api/v1/incidents/generativeai/suggestions',
            headers={'X-Apigateway-Api-Userinfo': token_encoded},
            query_string={'locale': 'es-CO'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(response.json, suggestions)
