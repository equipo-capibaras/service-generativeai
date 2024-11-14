from typing import cast
from unittest.mock import Mock

import responses
from faker import Faker
from requests import HTTPError
from unittest_parametrize import ParametrizedTestCase, parametrize

from models import Action, HistoryEntry, IncidentUpdateBody
from repositories.rest import RestIncidentRepository, TokenProvider


class TestRestIncidentRepository(ParametrizedTestCase):
    def setUp(self) -> None:
        self.faker = Faker()
        self.base_url = self.faker.url().rstrip('/')
        self.repo = RestIncidentRepository(self.base_url, None)

    def test_authenticated_post_without_token_provider(self) -> None:
        repo = RestIncidentRepository(self.base_url, None)

        with responses.RequestsMock() as rsps:
            rsps.post(self.base_url)
            repo.authenticated_post(self.base_url, body={})
            self.assertNotIn('Authorization', rsps.calls[0].request.headers)

    def test_authenticated_post_with_token_provider(self) -> None:
        token = self.faker.pystr()
        token_provider = Mock(TokenProvider)
        cast(Mock, token_provider.get_token).return_value = token

        repo = RestIncidentRepository(self.base_url, token_provider)

        with responses.RequestsMock() as rsps:
            rsps.post(self.base_url)
            repo.authenticated_post(self.base_url, body={})
            self.assertEqual(rsps.calls[0].request.headers['Authorization'], f'Bearer {token}')

    def test_update_success(self) -> None:
        client_id = cast(str, self.faker.uuid4())
        incident_id = cast(str, self.faker.uuid4())
        assigned_to_id = cast(str, self.faker.uuid4())
        update_body = IncidentUpdateBody(
            action=Action.AI_RESPONSE.value,
            description=self.faker.text(),
        )
        history_entry = HistoryEntry(
            incident_id=incident_id,
            client_id=client_id,
            seq=self.faker.random_int(),
            date=self.faker.past_datetime(),
            action=Action.AI_RESPONSE,
            description=self.faker.text(),
        )

        with responses.RequestsMock() as rsps:
            rsps.post(
                f'{self.base_url}/api/v1/clients/{client_id}/employees/{assigned_to_id}/incidents/{incident_id}/update',
                json={
                    'incident_id': history_entry.incident_id,
                    'client_id': history_entry.client_id,
                    'seq': history_entry.seq,
                    'date': history_entry.date.isoformat(),
                    'action': history_entry.action.value,
                    'description': history_entry.description,
                },
                status=200,
            )

            result = self.repo.update(client_id, incident_id, assigned_to_id, update_body)

        self.assertEqual(result, history_entry)

    def test_update_not_found(self) -> None:
        client_id = cast(str, self.faker.uuid4())
        incident_id = cast(str, self.faker.uuid4())
        assigned_to_id = cast(str, self.faker.uuid4())
        update_body = IncidentUpdateBody(
            action=Action.AI_RESPONSE.value,
            description=self.faker.text(),
        )

        with responses.RequestsMock() as rsps:
            rsps.post(
                f'{self.base_url}/api/v1/clients/{client_id}/employees/{assigned_to_id}/incidents/{incident_id}/update',
                json={'message': 'Incident not found', 'code': 404},
                status=404,
            )

            result = self.repo.update(client_id, incident_id, assigned_to_id, update_body)

        self.assertIsNone(result)

    @parametrize(
        'status',
        [
            (500,),
            (400,),
        ],
    )
    def test_update_unexpected_error(self, status: int) -> None:
        client_id = cast(str, self.faker.uuid4())
        incident_id = cast(str, self.faker.uuid4())
        assigned_to_id = cast(str, self.faker.uuid4())
        update_body = IncidentUpdateBody(
            action=Action.AI_RESPONSE.value,
            description=self.faker.text(),
        )

        with responses.RequestsMock() as rsps, self.assertRaises(HTTPError):
            rsps.post(
                f'{self.base_url}/api/v1/clients/{client_id}/employees/{assigned_to_id}/incidents/{incident_id}/update',
                status=status,
            )

            self.repo.update(client_id, incident_id, assigned_to_id, update_body)
