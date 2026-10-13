import pytest

from models import Resume
from render import render_pdf


@pytest.mark.parametrize(
    "data",
    [
        {},
        {
            "basics": {
                "name": "Jane Doe",
                "summary": "Engineer.",
                "location": {"city": "London"},
                "profiles": [{"network": "GitHub", "url": "https://github.com/jane"}],
            },
            "skills": [{"name": "Languages", "keywords": ["Python"]}],
            "education": [{"institution": "UCL", "startDate": "2016-09-01"}],
            "work": [
                {
                    "name": "Acme",
                    "position": "Engineer",
                    "startDate": "2020-01-01",
                    "highlights": ["Used **Python** & C#"],
                }
            ],
            "projects": [{"name": "Resumate", "description": "A **CV** tool"}],
        },
    ],
    ids=["empty", "populated"],
)
def test_renders_pdf(data):
    pdf = render_pdf(Resume.model_validate(data))

    assert pdf.startswith(b"%PDF")


def test_renders_without_typst_warnings(caplog):
    resume = Resume.model_validate(
        {
            "basics": {
                "phone": "+44",
                "profiles": [{"network": "GitHub", "url": "https://github.com/jane"}],
            }
        }
    )

    render_pdf(resume)

    assert caplog.records == []
