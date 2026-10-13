"""Pydantic models for the JSON Resume schema (https://jsonresume.org/schema)."""

import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


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
    start_date: datetime.date | None = None
    end_date: datetime.date | None = None
    summary: str | None = None
    highlights: list[str] = []


class Volunteer(JsonResumeModel):
    organization: str | None = None
    position: str | None = None
    url: str | None = None
    start_date: datetime.date | None = None
    end_date: datetime.date | None = None
    summary: str | None = None
    highlights: list[str] = []


class Education(JsonResumeModel):
    institution: str | None = None
    url: str | None = None
    area: str | None = None
    study_type: str | None = None
    start_date: datetime.date | None = None
    end_date: datetime.date | None = None
    score: str | None = None
    courses: list[str] = []


class Award(JsonResumeModel):
    title: str | None = None
    date: datetime.date | None = None
    awarder: str | None = None
    summary: str | None = None


class Certificate(JsonResumeModel):
    name: str | None = None
    date: datetime.date | None = None
    url: str | None = None
    issuer: str | None = None


class Publication(JsonResumeModel):
    name: str | None = None
    publisher: str | None = None
    release_date: datetime.date | None = None
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
    start_date: datetime.date | None = None
    end_date: datetime.date | None = None
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
