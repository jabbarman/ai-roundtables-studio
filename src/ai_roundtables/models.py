from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(slots=True)
class ParticipantConfig:
    name: str
    provider: str
    model: str
    prompt_file: str
    stance: str
    temperature: float | None = None


@dataclass(slots=True)
class ModeratorConfig:
    name: str
    prompt_file: str


@dataclass(slots=True)
class TurnRecord:
    speaker: str
    prompt: str
    response: str = ""
    provider: str = ""
    model: str = ""
    status: str = "pending"


@dataclass(slots=True)
class RoundtableConfig:
    slug: str
    title: str
    date: date
    audience: str
    format: str
    topic: str
    brief: str = ""
    moderator: ModeratorConfig | None = None
    participants: list[ParticipantConfig] = field(default_factory=list)
    editorial_goals: list[str] = field(default_factory=list)
    turns: int = 1
