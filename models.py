import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _new_id() -> str:
    return str(uuid.uuid4())[:8].upper()


@dataclass
class Contact:
    name: str
    email: str
    phone: str
    memo: str = ""
    id: str = field(default_factory=_new_id)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    REQUIRED_FIELDS = ["name", "email", "phone"]
    EDITABLE_FIELDS = ["name", "email", "phone", "memo"]
    FIELD_LABELS = {
        "name": "이름",
        "email": "이메일",
        "phone": "전화번호",
        "memo": "메모",
    }

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Contact":
        return cls(**data)
