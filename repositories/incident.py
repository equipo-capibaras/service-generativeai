from models import HistoryEntry, IncidentUpdateBody


class IncidentRepository:
    def update(self, client_id: str, incident_id: str, assigned_to_id: str, body: IncidentUpdateBody) -> HistoryEntry | None:
        raise NotImplementedError  # pragma: no cover
