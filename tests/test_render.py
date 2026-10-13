import pytest

from models import Resume
from render import MIN_FONT_SIZE, count_pages, render_pdf, render_to_fit


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
        {"skills": [{}], "education": [{}], "work": [{}], "projects": [{}]},
    ],
    ids=["empty", "populated", "entries-without-optional-fields"],
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


def resume_with_bullets(count: int) -> Resume:
    bullet = "Delivered a meaningful improvement to a system that mattered a lot."
    return Resume.model_validate(
        {"work": [{"name": "Acme", "highlights": [bullet] * count}]}
    )


def smallest_overflowing_resume() -> Resume:
    count = 1
    while count_pages(resume_with_bullets(count)) == 1:
        count += 1
    return resume_with_bullets(count)


@pytest.mark.parametrize(
    ("paper", "media_box"),
    [("a4", b"595.2756 841.8898"), ("us-letter", b"612 792")],
)
def test_renders_requested_paper_size(paper, media_box):
    pdf = render_pdf(Resume(), paper=paper)

    assert media_box in pdf


def test_counts_pages():
    assert count_pages(resume_with_bullets(1)) == 1
    assert count_pages(resume_with_bullets(200)) > 1


def test_fit_keeps_default_size_when_content_fits():
    rendered = render_to_fit(resume_with_bullets(1))

    assert rendered.font_size == 11
    assert rendered.pages == 1


def test_fit_shrinks_text_to_stay_within_page_limit():
    rendered = render_to_fit(smallest_overflowing_resume())

    assert MIN_FONT_SIZE <= rendered.font_size < 11
    assert rendered.pages == 1


def test_fit_respects_max_pages():
    rendered = render_to_fit(smallest_overflowing_resume(), max_pages=2)

    assert rendered.font_size == 11
    assert rendered.pages == 2


def test_fit_stops_at_minimum_size_when_content_cannot_fit():
    rendered = render_to_fit(resume_with_bullets(200))

    assert rendered.font_size == MIN_FONT_SIZE
    assert rendered.pages > 1
