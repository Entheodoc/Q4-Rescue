from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = REPO_ROOT / "documentation" / "project_status_snapshot_2026-03-15.pdf"
REPORT_DATE = "March 15, 2026"

PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN = 42

INK = colors.HexColor("#16233B")
INK_SOFT = colors.HexColor("#5A667A")
CREAM = colors.HexColor("#F7F1E8")
WHITE = colors.HexColor("#FFFFFF")
CARD = colors.HexColor("#FFFDFC")
MIST = colors.HexColor("#E7ECF3")
CORAL = colors.HexColor("#EF6B4A")
GOLD = colors.HexColor("#F4B844")
TEAL = colors.HexColor("#2E9B8C")
ROSE = colors.HexColor("#C74D44")
SKY = colors.HexColor("#D6E4F4")
SAGE = colors.HexColor("#DDEBE2")
BLUSH = colors.HexColor("#F6E0DA")
MIDNIGHT = colors.HexColor("#0D172A")


def _run_git(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True).strip()
    except Exception:
        return ""


def _git_status_counts() -> tuple[int, int]:
    output = _run_git("status", "--short")
    modified = 0
    untracked = 0
    for line in output.splitlines():
        code = line[:2]
        if code == "??":
            untracked += 1
        elif "M" in code:
            modified += 1
    return modified, untracked


def _recent_commits(limit: int = 4) -> list[str]:
    output = _run_git("log", "--oneline", "--decorate", f"-n{limit}")
    return [line.strip() for line in output.splitlines() if line.strip()]


@dataclass
class SnapshotMeta:
    branch: str
    head: str
    modified_files: int
    untracked_files: int
    recent_commits: list[str]


def get_snapshot_meta() -> SnapshotMeta:
    modified, untracked = _git_status_counts()
    return SnapshotMeta(
        branch=_run_git("rev-parse", "--abbrev-ref", "HEAD") or "main",
        head=_run_git("rev-parse", "--short", "HEAD") or "unknown",
        modified_files=modified,
        untracked_files=untracked,
        recent_commits=_recent_commits(),
    )


def register_fonts() -> dict[str, str]:
    candidates = {
        "body": (
            REPO_ROOT / ".missing",
            "/System/Library/Fonts/Avenir.ttc",
            "Helvetica",
        ),
        "display": (
            REPO_ROOT / ".missing",
            "/System/Library/Fonts/Avenir Next Condensed.ttc",
            "Helvetica-Bold",
        ),
        "strong": (
            REPO_ROOT / ".missing",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "Helvetica-Bold",
        ),
        "mono": (
            REPO_ROOT / ".missing",
            "/System/Library/Fonts/SFNSMono.ttf",
            "Courier",
        ),
    }

    registered: dict[str, str] = {}
    aliases = {
        "body": "SnapshotBody",
        "display": "SnapshotDisplay",
        "strong": "SnapshotStrong",
        "mono": "SnapshotMono",
    }

    for key, (_, path, fallback) in candidates.items():
        font_path = Path(path)
        alias = aliases[key]
        if font_path.exists():
            pdfmetrics.registerFont(TTFont(alias, str(font_path)))
            registered[key] = alias
        else:
            registered[key] = fallback

    return registered


def build_styles(fonts: dict[str, str]) -> dict[str, ParagraphStyle]:
    return {
        "cover_kicker": ParagraphStyle(
            "cover_kicker",
            fontName=fonts["strong"],
            fontSize=10,
            leading=12,
            textColor=GOLD,
            alignment=TA_LEFT,
        ),
        "cover_title": ParagraphStyle(
            "cover_title",
            fontName=fonts["display"],
            fontSize=34,
            leading=34,
            textColor=WHITE,
            alignment=TA_LEFT,
        ),
        "cover_body": ParagraphStyle(
            "cover_body",
            fontName=fonts["body"],
            fontSize=12.5,
            leading=18,
            textColor=colors.HexColor("#E7EBF1"),
            alignment=TA_LEFT,
        ),
        "page_kicker": ParagraphStyle(
            "page_kicker",
            fontName=fonts["strong"],
            fontSize=9.5,
            leading=12,
            textColor=CORAL,
            alignment=TA_LEFT,
        ),
        "page_title": ParagraphStyle(
            "page_title",
            fontName=fonts["display"],
            fontSize=24,
            leading=24,
            textColor=INK,
            alignment=TA_LEFT,
        ),
        "intro": ParagraphStyle(
            "intro",
            fontName=fonts["body"],
            fontSize=11.5,
            leading=16,
            textColor=INK_SOFT,
            alignment=TA_LEFT,
        ),
        "card_label": ParagraphStyle(
            "card_label",
            fontName=fonts["strong"],
            fontSize=8.5,
            leading=10,
            textColor=INK_SOFT,
            alignment=TA_LEFT,
        ),
        "card_title": ParagraphStyle(
            "card_title",
            fontName=fonts["strong"],
            fontSize=13,
            leading=16,
            textColor=INK,
            alignment=TA_LEFT,
        ),
        "card_body": ParagraphStyle(
            "card_body",
            fontName=fonts["body"],
            fontSize=10.2,
            leading=14.2,
            textColor=INK_SOFT,
            alignment=TA_LEFT,
        ),
        "small": ParagraphStyle(
            "small",
            fontName=fonts["body"],
            fontSize=8.5,
            leading=11,
            textColor=INK_SOFT,
            alignment=TA_LEFT,
        ),
        "code": ParagraphStyle(
            "code",
            fontName=fonts["mono"],
            fontSize=8.7,
            leading=12,
            textColor=WHITE,
            alignment=TA_LEFT,
        ),
        "chip": ParagraphStyle(
            "chip",
            fontName=fonts["strong"],
            fontSize=8.8,
            leading=10,
            textColor=WHITE,
            alignment=TA_CENTER,
        ),
    }


def draw_shadow(c: canvas.Canvas, x: float, y: float, width: float, height: float, radius: float = 20) -> None:
    c.saveState()
    if hasattr(c, "setFillAlpha"):
        c.setFillAlpha(0.08)
    c.setFillColor(colors.black)
    c.roundRect(x + 5, y - 5, width, height, radius, fill=1, stroke=0)
    c.restoreState()


def draw_card(
    c: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    fill_color=WHITE,
    stroke_color=None,
    radius: float = 22,
) -> None:
    draw_shadow(c, x, y, width, height, radius)
    c.saveState()
    c.setFillColor(fill_color)
    c.setStrokeColor(stroke_color or fill_color)
    c.roundRect(x, y, width, height, radius, fill=1, stroke=1 if stroke_color else 0)
    c.restoreState()


def draw_paragraph(
    c: canvas.Canvas,
    text: str,
    style: ParagraphStyle,
    x: float,
    top: float,
    width: float,
) -> float:
    paragraph = Paragraph(text, style)
    _, height = paragraph.wrap(width, PAGE_HEIGHT)
    paragraph.drawOn(c, x, top - height)
    return top - height


def draw_bullets(
    c: canvas.Canvas,
    items: list[str],
    style: ParagraphStyle,
    x: float,
    top: float,
    width: float,
    bullet_color=CORAL,
) -> float:
    cursor = top
    for item in items:
        c.saveState()
        c.setFillColor(bullet_color)
        c.circle(x + 4, cursor - 8, 2.5, fill=1, stroke=0)
        c.restoreState()
        cursor = draw_paragraph(c, item, style, x + 14, cursor, width - 14)
        cursor -= 7
    return cursor


def draw_chip(
    c: canvas.Canvas,
    text: str,
    style: ParagraphStyle,
    x: float,
    y: float,
    fill_color,
    text_color=WHITE,
) -> float:
    width = pdfmetrics.stringWidth(text, style.fontName, style.fontSize) + 24
    c.saveState()
    c.setFillColor(fill_color)
    c.roundRect(x, y, width, 24, 12, fill=1, stroke=0)
    c.restoreState()
    chip_style = ParagraphStyle(
        "chip_clone",
        parent=style,
        textColor=text_color,
        alignment=TA_CENTER,
    )
    draw_paragraph(c, text, chip_style, x, y + 17, width)
    return width


def draw_metric_card(
    c: canvas.Canvas,
    styles: dict[str, ParagraphStyle],
    fonts: dict[str, str],
    x: float,
    y: float,
    width: float,
    height: float,
    value: str,
    label: str,
    note: str,
    accent_color,
    tint_color,
) -> None:
    draw_card(c, x, y, width, height, fill_color=CARD)
    c.saveState()
    c.setFillColor(tint_color)
    c.roundRect(x, y + height - 16, width, 16, 22, fill=1, stroke=0)
    c.restoreState()

    c.setFillColor(accent_color)
    c.setFont(fonts["display"], 26)
    c.drawString(x + 18, y + height - 56, value)

    cursor = y + height - 72
    cursor = draw_paragraph(c, label, styles["card_title"], x + 18, cursor, width - 36)
    draw_paragraph(c, note, styles["small"], x + 18, cursor - 10, width - 36)


def draw_progress_bar(
    c: canvas.Canvas,
    styles: dict[str, ParagraphStyle],
    fonts: dict[str, str],
    x: float,
    y: float,
    width: float,
    label: str,
    percent: int,
    bar_color,
) -> None:
    draw_paragraph(c, label, styles["small"], x, y + 16, width - 40)
    c.setFont(fonts["strong"], 8.8)
    c.setFillColor(INK_SOFT)
    c.drawRightString(x + width, y + 4, f"{percent}%")
    c.setFillColor(MIST)
    c.roundRect(x, y - 8, width, 8, 4, fill=1, stroke=0)
    c.setFillColor(bar_color)
    c.roundRect(x, y - 8, width * (percent / 100), 8, 4, fill=1, stroke=0)


def draw_page_frame(c: canvas.Canvas, styles: dict[str, ParagraphStyle], page_number: int, title: str) -> None:
    c.setFillColor(CREAM)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    c.setFillColor(SKY)
    c.circle(PAGE_WIDTH - 34, PAGE_HEIGHT - 40, 48, fill=1, stroke=0)
    c.setFillColor(BLUSH)
    c.circle(PAGE_WIDTH - 86, PAGE_HEIGHT - 74, 22, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.roundRect(MARGIN, PAGE_HEIGHT - 54, 54, 6, 3, fill=1, stroke=0)
    draw_paragraph(c, "Q4-RESCUE STATUS SNAPSHOT", styles["page_kicker"], MARGIN, PAGE_HEIGHT - 64, 220)
    draw_paragraph(c, title, styles["page_title"], MARGIN, PAGE_HEIGHT - 86, 360)
    c.setFont(styles["small"].fontName, styles["small"].fontSize)
    c.setFillColor(INK_SOFT)
    c.drawRightString(PAGE_WIDTH - MARGIN, 24, f"Page {page_number}")


def draw_cover(c: canvas.Canvas, meta: SnapshotMeta, styles: dict[str, ParagraphStyle], fonts: dict[str, str]) -> None:
    c.setFillColor(CREAM)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

    c.setFillColor(INK)
    c.roundRect(-22, 188, PAGE_WIDTH + 44, PAGE_HEIGHT - 150, 34, fill=1, stroke=0)

    c.saveState()
    if hasattr(c, "setFillAlpha"):
        c.setFillAlpha(0.14)
    c.setStrokeColor(WHITE)
    for x in range(24, int(PAGE_WIDTH), 28):
        c.line(x, 220, x + 60, PAGE_HEIGHT)
    c.restoreState()

    c.setFillColor(CORAL)
    c.circle(PAGE_WIDTH - 36, PAGE_HEIGHT - 18, 94, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.circle(PAGE_WIDTH - 114, PAGE_HEIGHT - 126, 26, fill=1, stroke=0)
    c.setFillColor(TEAL)
    c.circle(86, 210, 58, fill=1, stroke=0)

    top = PAGE_HEIGHT - 92
    top = draw_paragraph(c, "PROJECT HEALTH MEMO / DESIGNED EXPORT", styles["cover_kicker"], 58, top, 260)
    top -= 12
    top = draw_paragraph(c, "Q4-Rescue<br/>Project Status Snapshot", styles["cover_title"], 58, top, 360)
    top -= 12
    draw_paragraph(
        c,
        "A polished stakeholder snapshot of where the platform stands today: what is shipping, what is still only scaffolded, and what should happen next.",
        styles["cover_body"],
        58,
        top,
        360,
    )

    chip_y = 256
    chip_x = 58
    for text, fill in (
        ("Backend foundation", CORAL),
        ("Case slice is real", TEAL),
        ("19 tests green", GOLD),
    ):
        width = draw_chip(c, text, styles["chip"], chip_x, chip_y, fill, text_color=WHITE if fill != GOLD else INK)
        chip_x += width + 10

    draw_card(c, 44, 44, PAGE_WIDTH - 88, 118, fill_color=WHITE)
    c.setFillColor(INK)
    c.setFont(fonts["strong"], 10)
    c.drawString(66, 132, "Prepared")
    c.drawString(232, 132, "Repository")
    c.drawString(414, 132, "Branch / HEAD")

    c.setFillColor(INK_SOFT)
    c.setFont(fonts["body"], 11)
    c.drawString(66, 112, REPORT_DATE)
    c.drawString(232, 112, "/Applications/Q4-Rescue")
    c.drawString(414, 112, f"{meta.branch} / {meta.head}")

    c.setFillColor(INK_SOFT)
    c.setFont(fonts["body"], 9.5)
    c.drawString(66, 82, "Working tree at time of review")
    c.drawString(232, 82, "Modified tracked files")
    c.drawString(414, 82, "Untracked files")

    c.setFillColor(INK)
    c.setFont(fonts["display"], 18)
    c.drawString(66, 56, "In-flight build")
    c.drawString(232, 56, str(meta.modified_files))
    c.drawString(414, 56, str(meta.untracked_files))


def draw_overview_page(c: canvas.Canvas, meta: SnapshotMeta, styles: dict[str, ParagraphStyle], fonts: dict[str, str]) -> None:
    draw_page_frame(c, styles, 2, "At A Glance")
    draw_paragraph(
        c,
        "Read this as a platform health memo, not a launch deck. The project has one meaningful vertical slice in place, a stronger technical core than the README implies, and a sizable amount of work still to land before it becomes an operational product.",
        styles["intro"],
        MARGIN,
        PAGE_HEIGHT - 116,
        PAGE_WIDTH - (MARGIN * 2),
    )

    card_y = 520
    card_w = 120
    gap = 12
    values = [
        ("19", "Tests passing", "Local .venv suite completed cleanly during review.", TEAL, SAGE),
        (str(meta.modified_files), "Tracked edits", "The repo is actively moving, not sitting in a release state.", CORAL, BLUSH),
        (str(meta.untracked_files), "New files", "Recent architecture and documentation work has not been fully committed.", GOLD, colors.HexColor("#F8EDD3")),
        ("1", "Strong live slice", "Case management is the one clearly implemented end-to-end surface.", INK, SKY),
    ]
    for index, item in enumerate(values):
        draw_metric_card(
            c,
            styles,
            fonts,
            MARGIN + (index * (card_w + gap)),
            card_y,
            card_w,
            120,
            *item,
        )

    draw_card(c, MARGIN, 282, 330, 210, fill_color=WHITE)
    draw_paragraph(c, "WHAT IS SOLID TODAY", styles["card_label"], MARGIN + 20, 470, 160)
    draw_paragraph(c, "The project can do real work right now", styles["card_title"], MARGIN + 20, 448, 290)
    draw_bullets(
        c,
        [
            "Boot a FastAPI backend and validate runtime settings.",
            "Run Alembic migrations automatically against Postgres.",
            "Create, list, retrieve, update, and archive cases.",
            "Enforce token auth, permission checks, request IDs, and audit logging.",
            "Persist a normalized rescue graph with shared provider and pharmacy records.",
        ],
        styles["card_body"],
        MARGIN + 20,
        422,
        290,
        bullet_color=TEAL,
    )

    draw_card(c, 390, 282, PAGE_WIDTH - 390 - MARGIN, 210, fill_color=WHITE)
    draw_paragraph(c, "DELIVERY READ", styles["card_label"], 410, 470, 120)
    draw_paragraph(c, "How mature each layer feels today", styles["card_title"], 410, 448, 150)
    draw_progress_bar(c, styles, fonts, 410, 398, 150, "Foundation strength", 78, TEAL)
    draw_progress_bar(c, styles, fonts, 410, 350, 150, "Product completeness", 36, CORAL)
    draw_progress_bar(c, styles, fonts, 410, 302, 150, "Release readiness", 32, GOLD)
    draw_paragraph(
        c,
        "Interpretation: the backend base is credible, but the broader operator product is still ahead of the code.",
        styles["small"],
        410,
        268,
        150,
    )


def draw_implemented_page(c: canvas.Canvas, styles: dict[str, ParagraphStyle]) -> None:
    draw_page_frame(c, styles, 3, "Implemented Surface")
    draw_paragraph(
        c,
        "The strongest signal in this repo is that the architecture is no longer speculative. The code now reflects a real service layer, real persistence, and real lifecycle rules for the case workflow.",
        styles["intro"],
        MARGIN,
        PAGE_HEIGHT - 116,
        PAGE_WIDTH - (MARGIN * 2),
    )

    cards = [
        (
            MARGIN,
            382,
            "Runtime and security",
            SKY,
            [
                "FastAPI app with startup validation and database initialization.",
                "Postgres-only runtime guardrails and SQLAlchemy URL normalization.",
                "Bearer-token auth with permission-scoped access.",
                "Request IDs are generated or propagated on every request.",
            ],
        ),
        (
            314,
            382,
            "Case API",
            BLUSH,
            [
                "Create, list, detail, status update, and archive routes are active.",
                "Routes now delegate to a service layer instead of reaching straight into persistence.",
                "Idempotency support protects repeated create requests.",
                "Audit events are recorded for sensitive reads and writes.",
            ],
        ),
        (
            MARGIN,
            110,
            "Domain rules",
            SAGE,
            [
                "Case lifecycle transitions are governed in domain code.",
                "Duplicate active cases for the same member are blocked.",
                "Measure uniqueness is validated per case.",
                "Medication relationships enforce one current prescriber and one refill-contact provider.",
            ],
        ),
        (
            314,
            110,
            "Persistence and observability",
            colors.HexColor("#F8EDD3"),
            [
                "The schema already models measures, meds, providers, pharmacies, tasks, barriers, and contact attempts.",
                "Provider and pharmacy identities can be reused across cases.",
                "Audit and idempotency tables are now first-class parts of the backend.",
                "CI is configured to run tests against Postgres.",
            ],
        ),
    ]

    for x, y, title, tint, bullets in cards:
        draw_card(c, x, y, 256, 238, fill_color=WHITE)
        c.setFillColor(tint)
        c.roundRect(x, y + 222, 256, 16, 22, fill=1, stroke=0)
        draw_paragraph(c, title.upper(), styles["card_label"], x + 18, y + 208, 220)
        draw_paragraph(c, title, styles["card_title"], x + 18, y + 188, 220)
        draw_bullets(c, bullets, styles["card_body"], x + 18, y + 162, 220, bullet_color=CORAL)


def draw_gap_page(c: canvas.Canvas, styles: dict[str, ParagraphStyle], fonts: dict[str, str]) -> None:
    draw_page_frame(c, styles, 4, "Gaps, Placeholders, And Risk")
    draw_paragraph(
        c,
        "The persistence model is ahead of the exposed product surface. That is promising architecturally, but it also means some of the repo's ambition still exists mostly in schema, documents, and empty modules.",
        styles["intro"],
        MARGIN,
        PAGE_HEIGHT - 116,
        PAGE_WIDTH - (MARGIN * 2),
    )

    draw_card(c, MARGIN, 264, 250, 410, fill_color=WHITE)
    draw_paragraph(c, "STILL MISSING", styles["card_label"], MARGIN + 18, 650, 140)
    draw_paragraph(c, "Major product capabilities not yet wired in", styles["card_title"], MARGIN + 18, 628, 210)
    draw_bullets(
        c,
        [
            "Completed eligibility and intake ingestion.",
            "Task-management API and operator work queue.",
            "Barrier and contact-attempt workflows.",
            "Governed domain-event stream for downstream automation.",
            "Projection and reporting layer for dashboards.",
            "Frontend or operational interface.",
            "Voice-agent integration.",
            "Broad workflow-level test coverage beyond the case slice.",
        ],
        styles["card_body"],
        MARGIN + 18,
        598,
        210,
        bullet_color=ROSE,
    )

    draw_card(c, 308, 386, PAGE_WIDTH - 308 - MARGIN, 288, fill_color=MIDNIGHT)
    draw_paragraph(c, "PLACEHOLDER MODULES", styles["card_label"], 326, 650, 180)
    code_lines = [
        "app/api/routes/eligibility.py",
        "app/application/commands/ingest_eligibility_row.py",
        "app/automation/dispatcher.py",
        "app/automation/handlers/case_created.py",
        "app/projection/models.py",
        "app/projection/updater.py",
        "app/rules/eligibility.py",
        "app/domain/events.py",
    ]
    cursor = 620
    for line in code_lines:
        cursor = draw_paragraph(c, line, styles["code"], 326, cursor, 220)
        cursor -= 5

    draw_card(c, 308, 264, PAGE_WIDTH - 308 - MARGIN, 104, fill_color=WHITE)
    draw_paragraph(c, "PRIMARY RISKS", styles["card_label"], 326, 346, 120)
    draw_bullets(
        c,
        [
            "Large in-flight change set on main reduces release confidence.",
            "Documentation and runnable product are not perfectly aligned.",
            "Feature surface in the schema is wider than the API actually exposes.",
        ],
        styles["card_body"],
        326,
        324,
        220,
        bullet_color=GOLD,
    )

    c.saveState()
    c.setFillColor(INK)
    c.roundRect(MARGIN, 90, PAGE_WIDTH - (MARGIN * 2), 122, 26, fill=1, stroke=0)
    c.restoreState()
    draw_paragraph(c, "WHAT THIS MEANS OPERATIONALLY", styles["cover_kicker"], MARGIN + 24, 186, 220)
    draw_paragraph(
        c,
        "The system can manage case records credibly today, but it cannot yet support a full rescue operations team end to end. The next milestone has to be a workflow milestone, not just more schema or documentation.",
        ParagraphStyle(
            "impact_body",
            parent=styles["card_body"],
            fontName=styles["card_body"].fontName,
            textColor=WHITE,
            fontSize=11,
            leading=16,
        ),
        MARGIN + 24,
        162,
        PAGE_WIDTH - (MARGIN * 2) - 48,
    )


def draw_verification_page(c: canvas.Canvas, meta: SnapshotMeta, styles: dict[str, ParagraphStyle]) -> None:
    draw_page_frame(c, styles, 5, "Verification And Evidence")
    draw_paragraph(
        c,
        "This snapshot was grounded in the repo itself: git state, core runtime files, persistence, tests, and active docs were all reviewed before the summary was written.",
        styles["intro"],
        MARGIN,
        PAGE_HEIGHT - 116,
        PAGE_WIDTH - (MARGIN * 2),
    )

    draw_card(c, MARGIN, 410, 250, 264, fill_color=WHITE)
    draw_paragraph(c, "VERIFICATION PERFORMED", styles["card_label"], MARGIN + 18, 650, 150)
    draw_bullets(
        c,
        [
            "Inspected git status, branch state, and recent visible commit history.",
            "Reviewed runtime, service, API, security, schema, and test files.",
            "Confirmed CI is configured to run tests against Postgres.",
            "Ran the local test suite inside the project virtual environment.",
        ],
        styles["card_body"],
        MARGIN + 18,
        628,
        210,
        bullet_color=TEAL,
    )

    draw_card(c, 308, 410, PAGE_WIDTH - 308 - MARGIN, 264, fill_color=MIDNIGHT)
    draw_paragraph(c, "TEST COMMAND", styles["card_label"], 326, 650, 140)
    draw_paragraph(
        c,
        ".venv/bin/python -m unittest discover -s tests -p 'test*.py' -q",
        styles["code"],
        326,
        626,
        220,
    )
    draw_paragraph(
        c,
        "Result: 19 tests passed. The system Python in this session did not have project dependencies installed, but the repository virtual environment did.",
        ParagraphStyle(
            "code_note",
            parent=styles["card_body"],
            textColor=WHITE,
        ),
        326,
        578,
        220,
    )
    draw_paragraph(
        c,
        "Environment note: the docker CLI was not available in this terminal session, so live local container status could not be confirmed from here.",
        ParagraphStyle(
            "code_note_two",
            parent=styles["small"],
            textColor=colors.HexColor("#C8D2E3"),
        ),
        326,
        518,
        220,
    )

    draw_card(c, MARGIN, 200, 250, 182, fill_color=WHITE)
    draw_paragraph(c, "EVIDENCE BASE", styles["card_label"], MARGIN + 18, 360, 120)
    draw_bullets(
        c,
        [
            "app/main.py",
            "app/api/routes/case.py",
            "app/application/services/case_service.py",
            "app/persistence/schema.sql",
            "tests/test_case_api.py",
            ".github/workflows/ci.yml",
        ],
        styles["card_body"],
        MARGIN + 18,
        338,
        210,
        bullet_color=CORAL,
    )

    draw_card(c, 308, 200, PAGE_WIDTH - 308 - MARGIN, 182, fill_color=WHITE)
    draw_paragraph(c, "RECENT REPO MOVEMENT", styles["card_label"], 326, 360, 170)
    cursor = 338
    for line in meta.recent_commits[:4]:
        cursor = draw_paragraph(c, line, styles["small"], 326, cursor, 220)
        cursor -= 8

    draw_card(c, MARGIN, 78, PAGE_WIDTH - (MARGIN * 2), 94, fill_color=WHITE)
    draw_paragraph(c, "DOCUMENTATION REALITY CHECK", styles["card_label"], MARGIN + 18, 150, 180)
    draw_paragraph(
        c,
        "The README understates implementation depth, while the master documentation describes a broader target-state platform than the current app exposes. The code is the better source of truth for current capability.",
        styles["card_body"],
        MARGIN + 18,
        126,
        PAGE_WIDTH - (MARGIN * 2) - 36,
    )


def draw_roadmap_page(c: canvas.Canvas, styles: dict[str, ParagraphStyle], fonts: dict[str, str]) -> None:
    draw_page_frame(c, styles, 6, "Recommended Next Moves")
    draw_paragraph(
        c,
        "The next phase should make the product more operable, not just more modeled. That means choosing the next workflow slice and carrying it all the way through APIs, tests, and release hygiene.",
        styles["intro"],
        MARGIN,
        PAGE_HEIGHT - 116,
        PAGE_WIDTH - (MARGIN * 2),
    )

    steps = [
        ("01", "Stabilize the branch", "Commit and review the architecture shift so the current progress is easier to reason about and safer to ship.", SKY),
        ("02", "Choose the next slice", "Pick eligibility intake or operator tasking as the next end-to-end milestone and align code around it.", BLUSH),
        ("03", "Expose the workflow", "Build API surfaces for the next slice instead of extending only the schema and docs.", SAGE),
        ("04", "Test the behavior", "Add targeted workflow tests that prove the next slice works in realistic sequences.", colors.HexColor("#F8EDD3")),
        ("05", "Tighten the docs", "Bring the README in line with the current code so stakeholders get a truthful repo snapshot quickly.", SKY),
        ("06", "Improve release hygiene", "Clarify local setup, migration flow, runtime env requirements, and deployment expectations.", BLUSH),
    ]

    positions = [
        (MARGIN, 458),
        (314, 458),
        (MARGIN, 314),
        (314, 314),
        (MARGIN, 170),
        (314, 170),
    ]

    for (number, title, body, tint), (x, y) in zip(steps, positions, strict=True):
        draw_card(c, x, y, 256, 118, fill_color=WHITE)
        c.setFillColor(tint)
        c.roundRect(x, y + 102, 256, 16, 22, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont(fonts["display"], 20)
        c.drawString(x + 18, y + 68, number)
        draw_paragraph(c, title, styles["card_title"], x + 62, y + 88, 176)
        draw_paragraph(c, body, styles["small"], x + 18, y + 54, 220)

    c.saveState()
    c.setFillColor(INK)
    c.roundRect(MARGIN, 54, PAGE_WIDTH - (MARGIN * 2), 88, 24, fill=1, stroke=0)
    c.restoreState()
    draw_paragraph(c, "BOTTOM LINE", styles["cover_kicker"], MARGIN + 20, 120, 150)
    draw_paragraph(
        c,
        "Q4-Rescue is past scaffold stage. The case-management backend is real, tested, and worth building on. What it needs next is product completion around that strong core.",
        ParagraphStyle(
            "verdict",
            parent=styles["card_body"],
            textColor=WHITE,
            fontSize=11.5,
            leading=16,
        ),
        MARGIN + 20,
        98,
        PAGE_WIDTH - (MARGIN * 2) - 40,
    )


def generate_pdf() -> Path:
    fonts = register_fonts()
    styles = build_styles(fonts)
    meta = get_snapshot_meta()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT_PATH), pagesize=letter)
    c.setTitle("Q4-Rescue Project Status Snapshot")
    c.setAuthor("OpenAI Codex")
    c.setSubject("Designed project status report")

    draw_cover(c, meta, styles, fonts)
    c.showPage()
    draw_overview_page(c, meta, styles, fonts)
    c.showPage()
    draw_implemented_page(c, styles)
    c.showPage()
    draw_gap_page(c, styles, fonts)
    c.showPage()
    draw_verification_page(c, meta, styles)
    c.showPage()
    draw_roadmap_page(c, styles, fonts)
    c.save()

    return OUTPUT_PATH


if __name__ == "__main__":
    output_path = generate_pdf()
    print(output_path)
