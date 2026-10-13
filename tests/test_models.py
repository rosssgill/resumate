import json
from datetime import date

import pytest
from pydantic import ValidationError

from models import Resume

SAMPLE = {
    "basics": {
        "name": "Jane Doe",
        "label": "Software Engineer",
        "email": "jane@example.com",
        "location": {"city": "London", "countryCode": "GB"},
        "profiles": [{"network": "GitHub", "username": "janedoe"}],
    },
    "work": [
        {
            "name": "Acme",
            "position": "Engineer",
            "startDate": "2020-01-01",
            "endDate": "2023-06-30",
            "highlights": ["Shipped things"],
        }
    ],
    "education": [
        {"institution": "UCL", "studyType": "BSc", "startDate": "2016-09-01"}
    ],
    "skills": [{"name": "Python", "keywords": ["pydantic", "typer"]}],
    "projects": [{"name": "Resumate", "roles": ["Author"]}],
}


def test_parses_camel_case_fields():
    resume = Resume.model_validate_json(json.dumps(SAMPLE))

    assert resume.basics.location.country_code == "GB"
    assert resume.basics.profiles[0].username == "janedoe"
    assert resume.work[0].start_date == date(2020, 1, 1)
    assert resume.education[0].study_type == "BSc"


def test_empty_resume_is_valid():
    resume = Resume.model_validate({})

    assert resume.basics.name is None
    assert resume.work == []


@pytest.mark.parametrize(
    "value",
    ["2023", "2023-04", "April 2023", "2023/04/29", 0, 1700006400, "1700006400"],
)
def test_rejects_dates_that_are_not_full_iso8601(value):
    with pytest.raises(ValidationError):
        Resume.model_validate({"work": [{"startDate": value}]})


def test_keeps_unknown_fields():
    resume = Resume.model_validate({"basics": {"name": "Jane", "pronouns": "she/her"}})

    assert resume.model_dump(by_alias=True)["basics"]["pronouns"] == "she/her"


def test_round_trips_to_json_resume_format():
    resume = Resume.model_validate(SAMPLE)

    dumped = resume.model_dump(mode="json", by_alias=True, exclude_defaults=True)

    assert dumped == SAMPLE
