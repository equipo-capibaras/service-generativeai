from typing import Any, cast
from unittest.mock import Mock

from faker import Faker
from unittest_parametrize import ParametrizedTestCase

from app import create_app
from models import Action, Channel, Plan, Role
from repositories import IncidentRepository


class TestIncidentsAIReponse(ParametrizedTestCase):
    def setUp(self) -> None:
        self.faker = Faker()
        self.app = create_app()
        self.client = self.app.test_client()
        self.incident_repo_mock = Mock(IncidentRepository)

    def gen_random_event_data(self, channel: Channel | None = None) -> dict[str, Any]:
        return {
            'id': cast(str, self.faker.uuid4()),
            'name': self.faker.sentence(3),
            'channel': channel or self.faker.random_element(list(Channel)),
            'language': self.faker.random_element(['es', 'pt']),
            'reportedBy': {
                'id': cast(str, self.faker.uuid4()),
                'name': self.faker.name(),
                'email': self.faker.email(),
                'role': Role.USER,
            },
            'createdBy': {
                'id': cast(str, self.faker.uuid4()),
                'name': self.faker.name(),
                'email': self.faker.email(),
                'role': Role.USER,
            },
            'assignedTo': {
                'id': cast(str, self.faker.uuid4()),
                'name': self.faker.name(),
                'email': self.faker.email(),
                'role': Role.AGENT,
            },
            'history': [
                {
                    'seq': 0,
                    'date': self.faker.past_datetime().isoformat().replace('+00:00', 'Z'),
                    'action': Action.CREATED.value,
                    'description': self.faker.text(200),
                },
            ],
            'client': {
                'id': cast(str, self.faker.uuid4()),
                'name': self.faker.company(),
                'emailIncidents': self.faker.email(),
                'plan': self.faker.random_element(list(Plan)),
            },
        }

    def test_incident_ai_response_created(self) -> None:
        data = self.gen_random_event_data(Channel.MOBILE)

        with self.app.container.incident_repo.override(self.incident_repo_mock):
            response = self.client.get('/api/v1/incident-update/generativeai', json=data)

        self.incident_repo_mock.update.assert_called_once()
        self.assertEqual(response.status_code, 200)

        expected_response = {'message': 'Event processed.', 'code': 200}
        self.assertEqual(response.json, expected_response)
