import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import typst

from core.config import Paper, Settings
from models import Resume

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent / "templates"
FONTS_DIR = Path(__file__).parent / "fonts"
TEMPLATE = TEMPLATES_DIR / "cv.typ"


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


def render_pdf(resume: Resume, *, paper: Paper, font_size: float) -> bytes:
    pdf, warnings = typst.compile_with_warnings(
        TEMPLATE, **_typst_options(resume, paper, font_size)
    )
    for warning in warnings:
        logger.warning("Typst: %s", warning)
    return pdf


def count_pages(resume: Resume, *, paper: Paper, font_size: float) -> int:
    return int(
        typst.query(
            TEMPLATE,
            "<page-count>",
            field="value",
            one=True,
            **_typst_options(resume, paper, font_size),
        )
    )


def render_to_fit(resume: Resume, settings: Settings) -> RenderedResume:
    """Render at the largest font size, down to the minimum, that fits max_pages."""
    paper = settings.paper
    font_size = settings.default_font_size
    pages = count_pages(resume, paper=paper, font_size=font_size)
    while pages > settings.max_pages and font_size > settings.min_font_size:
        font_size = max(font_size - settings.font_size_step, settings.min_font_size)
        pages = count_pages(resume, paper=paper, font_size=font_size)
    return RenderedResume(
        pdf=render_pdf(resume, paper=paper, font_size=font_size),
        pages=pages,
        font_size=font_size,
    )
