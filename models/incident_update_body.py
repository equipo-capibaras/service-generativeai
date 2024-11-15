from dataclasses import dataclass, field

import marshmallow.validate

from models import Action


@dataclass
class IncidentUpdateBody:
    action: str = field(metadata={'validate': [marshmallow.validate.OneOf([Action.AI_RESPONSE])]})
    description: str = field(metadata={'validate': marshmallow.validate.Length(min=1, max=1000)})
