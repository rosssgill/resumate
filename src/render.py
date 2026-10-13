import logging
from pathlib import Path

import typst

from models import Resume

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent / "templates"
FONTS_DIR = Path(__file__).parent / "fonts"


def render_pdf(resume: Resume, template: Path = TEMPLATES_DIR / "cv.typ") -> bytes:
    resume_json = resume.model_dump_json(by_alias=True, exclude_none=True)
    # System fonts are ignored so output is identical on every machine
    pdf, warnings = typst.compile_with_warnings(
        template,
        font_paths=[FONTS_DIR],
        ignore_system_fonts=True,
        sys_inputs={"resume": resume_json},
    )
    for warning in warnings:
        logger.warning("Typst: %s", warning)
    return pdf
