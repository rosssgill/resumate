import logging
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

import typst

from models import Resume

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent / "templates"
FONTS_DIR = Path(__file__).parent / "fonts"
TEMPLATE = TEMPLATES_DIR / "cv.typ"

DEFAULT_FONT_SIZE = 11.0
MIN_FONT_SIZE = 10.0
FONT_SIZE_STEP = 0.25


class Paper(StrEnum):
    A4 = "a4"
    US_LETTER = "us-letter"


@dataclass(frozen=True)
class RenderedResume:
    pdf: bytes
    pages: int
    font_size: float


def _typst_options(resume: Resume, paper: Paper, font_size: float) -> dict[str, Any]:
    return {
        # System fonts are ignored so output is identical on every machine
        "font_paths": [FONTS_DIR],
        "ignore_system_fonts": True,
        "sys_inputs": {
            "resume": resume.model_dump_json(by_alias=True, exclude_none=True),
            "paper": paper,
            "font-size": str(font_size),
        },
    }


def render_pdf(
    resume: Resume,
    *,
    paper: Paper = Paper.A4,
    font_size: float = DEFAULT_FONT_SIZE,
) -> bytes:
    pdf, warnings = typst.compile_with_warnings(
        TEMPLATE, **_typst_options(resume, paper, font_size)
    )
    for warning in warnings:
        logger.warning("Typst: %s", warning)
    return pdf


def count_pages(
    resume: Resume,
    *,
    paper: Paper = Paper.A4,
    font_size: float = DEFAULT_FONT_SIZE,
) -> int:
    return int(
        typst.query(
            TEMPLATE,
            "<page-count>",
            field="value",
            one=True,
            **_typst_options(resume, paper, font_size),
        )
    )


def render_to_fit(
    resume: Resume, *, max_pages: int = 1, paper: Paper = Paper.A4
) -> RenderedResume:
    """Render at the largest font size (down to MIN_FONT_SIZE) that fits max_pages."""
    font_size = DEFAULT_FONT_SIZE
    pages = count_pages(resume, paper=paper, font_size=font_size)
    while pages > max_pages and font_size > MIN_FONT_SIZE:
        font_size -= FONT_SIZE_STEP
        pages = count_pages(resume, paper=paper, font_size=font_size)
    pdf = render_pdf(resume, paper=paper, font_size=font_size)
    return RenderedResume(pdf=pdf, pages=pages, font_size=font_size)
