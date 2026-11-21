from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models import JobApplication, User
from app.schemas.analytics import KpiSummary
from app.services.report_common import now_wib

INK = colors.HexColor("#0F172A")
MUTED = colors.HexColor("#475569")
GRID = colors.HexColor("#CBD5E1")
ROW_ALT = colors.HexColor("#F8FAFC")


def _paragraph(value: object, style: ParagraphStyle) -> Paragraph:
    text = escape(str(value)) if value not in (None, "") else "-"
    return Paragraph(text, style)


def _link_paragraph(url: str | None, style: ParagraphStyle) -> Paragraph:
    if not url:
        return Paragraph("-", style)
    safe_url = escape(url, {'"': "&quot;"})
    return Paragraph(f'<link href="{safe_url}" color="#0369A1">{safe_url}</link>', style)


def build_pdf_report(
    applications: list[JobApplication],
    user: User,
    filter_summary: str,
    kpi: KpiSummary,
) -> bytes:
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
        title="Laporan Riwayat Lamaran Kerja",
        author="KarirTrack",
    )

    base = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "KarirTrackTitle",
        parent=base["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=INK,
        alignment=0,
        spaceAfter=4,
    )
    meta_style = ParagraphStyle(
        "KarirTrackMeta",
        parent=base["Normal"],
        fontSize=8.5,
        leading=12,
        textColor=MUTED,
    )
    section_style = ParagraphStyle(
        "KarirTrackSection",
        parent=base["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=INK,
        spaceBefore=8,
        spaceAfter=6,
    )
    cell_style = ParagraphStyle(
        "KarirTrackCell",
        parent=base["Normal"],
        fontSize=7.2,
        leading=8.8,
        textColor=INK,
    )
    header_style = ParagraphStyle(
        "KarirTrackHeader",
        parent=cell_style,
        fontName="Helvetica-Bold",
        textColor=colors.white,
        alignment=1,
    )
    empty_style = ParagraphStyle(
        "KarirTrackEmpty",
        parent=cell_style,
        fontName="Helvetica-Oblique",
        textColor=MUTED,
    )

    story: list[object] = [
        Paragraph("Laporan Riwayat Lamaran Kerja", title_style),
        Paragraph(
            f"<b>{escape(user.full_name)}</b> &nbsp;|&nbsp; {escape(user.email)}",
            meta_style,
        ),
        Paragraph(
            f"Dicetak: {now_wib():%Y-%m-%d %H:%M} WIB &nbsp;|&nbsp; "
            f"Filter: {escape(filter_summary)}",
            meta_style,
        ),
        Spacer(1, 8),
    ]

    summary_data = [
        [
            Paragraph(f"<b>{kpi.total}</b><br/>Total Lamaran", header_style),
            Paragraph(f"<b>{kpi.interview_count}</b><br/>Pernah Interview", header_style),
            Paragraph(f"<b>{kpi.offerings}</b><br/>Offering", header_style),
            Paragraph(f"<b>{kpi.rejected}</b><br/>Rejected", header_style),
        ]
    ]
    summary_table = Table(summary_data, colWidths=[190, 190, 190, 190])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), INK),
                ("BOX", (0, 0), (-1, -1), 0.5, INK),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#334155")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.extend([summary_table, Spacer(1, 10), Paragraph("Data Lamaran", section_style)])

    header_row = [
        Paragraph("No", header_style),
        Paragraph("Perusahaan", header_style),
        Paragraph("Posisi", header_style),
        Paragraph("Status", header_style),
        Paragraph("Portal", header_style),
        Paragraph("Model", header_style),
        Paragraph("Tanggal", header_style),
        Paragraph("Gaji", header_style),
        Paragraph("Link", header_style),
        Paragraph("Catatan", header_style),
    ]

    table_data: list[list[object]] = [header_row]
    for index, application in enumerate(applications, start=1):
        table_data.append(
            [
                Paragraph(str(index), cell_style),
                _paragraph(application.company_name, cell_style),
                _paragraph(application.position_title, cell_style),
                _paragraph(application.status, cell_style),
                _paragraph(application.job_portal, cell_style),
                _paragraph(application.work_model, cell_style),
                Paragraph(application.applied_date.strftime("%Y-%m-%d"), cell_style),
                _paragraph(application.salary_range, cell_style),
                _link_paragraph(application.job_url, cell_style),
                _paragraph(application.notes, cell_style),
            ]
        )

    if len(table_data) == 1:
        table_data.append(
            [
                Paragraph("Tidak ada data lamaran untuk filter ini.", empty_style),
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ]
        )

    column_widths = [22, 98, 104, 62, 68, 44, 54, 64, 92, 154]
    data_table = Table(table_data, colWidths=column_widths, repeatRows=1)
    table_style = [
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]
    for row_index in range(1, len(table_data)):
        if row_index % 2 == 0:
            table_style.append(("BACKGROUND", (0, row_index), (-1, row_index), ROW_ALT))
    data_table.setStyle(TableStyle(table_style))
    story.append(data_table)

    document.build(story)
    return buffer.getvalue()
