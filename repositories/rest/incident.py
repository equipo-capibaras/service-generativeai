from dataclasses import asdict
from typing import Any, cast

import dacite
import requests

from models import HistoryEntry, IncidentUpdateBody
from repositories import IncidentRepository

from .base import RestBaseRepository
from .util import TokenProvider


class RestIncidentRepository(IncidentRepository, RestBaseRepository):
    def __init__(self, base_url: str, token_provider: TokenProvider | None) -> None:
        RestBaseRepository.__init__(self, base_url, token_provider)

    def update(self, client_id: str, incident_id: str, assigned_to_id: str, body: IncidentUpdateBody) -> HistoryEntry | None:
        dict_body = asdict(body)
        resp = self.authenticated_post(
            url=f'{self.base_url}/api/v1/clients/{client_id}/employees/{assigned_to_id}/incidents/{incident_id}/update',
            body=dict_body,
        )

        if resp.status_code == requests.codes.ok:
            data = cast(dict[str, Any], resp.json())
            return dacite.from_dict(data_class=HistoryEntry, data=data)

        if resp.status_code == requests.codes.not_found:
            return None

        self.unexpected_error(resp)  # noqa: RET503
