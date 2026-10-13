"""Pydantic models for the JSON Resume schema (https://jsonresume.org/schema)."""

import datetime
import re
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field
from pydantic.alias_generators import to_camel

ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _require_iso_date_string(value: Any) -> Any:
    # Pydantic would otherwise also accept Unix timestamps as dates
    if isinstance(value, datetime.date) or (
        isinstance(value, str) and ISO_DATE_PATTERN.match(value)
    ):
        return value
    raise ValueError("date must be in YYYY-MM-DD format")


IsoDate = Annotated[datetime.date, BeforeValidator(_require_iso_date_string)]


class JsonResumeModel(BaseModel):
    # The schema allows extra properties everywhere, so keep rather than drop them
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="allow"
    )


class Location(JsonResumeModel):
    address: str | None = None
    postal_code: str | None = None
    city: str | None = None
    country_code: str | None = None
    region: str | None = None


class Profile(JsonResumeModel):
    network: str | None = None
    username: str | None = None
    url: str | None = None


class Basics(JsonResumeModel):
    name: str | None = None
    label: str | None = None
    image: str | None = None
    email: str | None = None
    phone: str | None = None
    url: str | None = None
    summary: str | None = None
    location: Location = Field(default_factory=Location)
    profiles: list[Profile] = []


class Work(JsonResumeModel):
    name: str | None = None
    location: str | None = None
    description: str | None = None
    position: str | None = None
    url: str | None = None
    start_date: IsoDate | None = None
    end_date: IsoDate | None = None
    summary: str | None = None
    highlights: list[str] = []


class Volunteer(JsonResumeModel):
    organization: str | None = None
    position: str | None = None
    url: str | None = None
    start_date: IsoDate | None = None
    end_date: IsoDate | None = None
    summary: str | None = None
    highlights: list[str] = []


class Education(JsonResumeModel):
    institution: str | None = None
    url: str | None = None
    area: str | None = None
    study_type: str | None = None
    start_date: IsoDate | None = None
    end_date: IsoDate | None = None
    score: str | None = None
    courses: list[str] = []


class Award(JsonResumeModel):
    title: str | None = None
    date: IsoDate | None = None
    awarder: str | None = None
    summary: str | None = None


class Certificate(JsonResumeModel):
    name: str | None = None
    date: IsoDate | None = None
    url: str | None = None
    issuer: str | None = None


class Publication(JsonResumeModel):
    name: str | None = None
    publisher: str | None = None
    release_date: IsoDate | None = None
    url: str | None = None
    summary: str | None = None


class Skill(JsonResumeModel):
    name: str | None = None
    level: str | None = None
    keywords: list[str] = []


class Language(JsonResumeModel):
    language: str | None = None
    fluency: str | None = None


class Interest(JsonResumeModel):
    name: str | None = None
    keywords: list[str] = []


class Reference(JsonResumeModel):
    name: str | None = None
    reference: str | None = None


class Project(JsonResumeModel):
    name: str | None = None
    description: str | None = None
    highlights: list[str] = []
    keywords: list[str] = []
    start_date: IsoDate | None = None
    end_date: IsoDate | None = None
    url: str | None = None
    roles: list[str] = []
    entity: str | None = None
    type: str | None = None


class Meta(JsonResumeModel):
    canonical: str | None = None
    version: str | None = None
    last_modified: str | None = None


class Resume(JsonResumeModel):
    basics: Basics = Field(default_factory=Basics)
    work: list[Work] = []
    volunteer: list[Volunteer] = []
    education: list[Education] = []
    awards: list[Award] = []
    certificates: list[Certificate] = []
    publications: list[Publication] = []
    skills: list[Skill] = []
    languages: list[Language] = []
    interests: list[Interest] = []
    references: list[Reference] = []
    projects: list[Project] = []
    meta: Meta = Field(default_factory=Meta)
