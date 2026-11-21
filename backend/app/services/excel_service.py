from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from app.models import JobApplication, User
from app.schemas.analytics import KpiSummary
from app.services.report_common import now_wib

HEADER_FILL = PatternFill("solid", fgColor="0F172A")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=10)
TITLE_FONT = Font(bold=True, size=16, color="0F172A")
SUBTITLE_FONT = Font(bold=True, size=11, color="0F172A")
THIN = Side(style="thin", color="CBD5E1")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

STATUS_FILLS = {
    "Applied": "DBEAFE",
    "Screening": "E0E7FF",
    "Technical Test": "FEF3C7",
    "HR Interview": "FDE68A",
    "User Interview": "FCD34D",
    "Offering": "BBF7D0",
    "Rejected": "FECACA",
    "Ghosted": "E5E7EB",
}


def _style_header(worksheet, row: int) -> None:
    for cell in worksheet[row]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER
    worksheet.row_dimensions[row].height = 26


def _autosize(worksheet, max_width: int = 45) -> None:
    for column_index, column in enumerate(worksheet.columns, start=1):
        longest = max(len(str(cell.value or "")) for cell in column)
        width = min(max(longest + 2, 12), max_width)
        worksheet.column_dimensions[get_column_letter(column_index)].width = width


def build_excel_report(
    applications: list[JobApplication],
    user: User,
    filter_summary: str,
    kpi: KpiSummary,
) -> bytes:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Data Lamaran"

    headers = [
        "No",
        "Perusahaan",
        "Posisi",
        "Status",
        "Portal",
        "Model Kerja",
        "Tanggal Melamar",
        "Rentang Gaji",
        "URL Lowongan",
        "Catatan",
        "Terakhir Update",
    ]
    worksheet.append(headers)
    _style_header(worksheet, 1)

    for index, application in enumerate(applications, start=1):
        worksheet.append(
            [
                index,
                application.company_name,
                application.position_title,
                application.status,
                application.job_portal,
                application.work_model,
                application.applied_date,
                application.salary_range or "-",
                application.job_url or "-",
                application.notes or "-",
                application.updated_at,
            ]
        )
        row = worksheet.max_row
        worksheet.cell(row=row, column=7).number_format = "yyyy-mm-dd"
        worksheet.cell(row=row, column=11).number_format = "yyyy-mm-dd hh:mm"
        status_cell = worksheet.cell(row=row, column=4)
        status_cell.fill = PatternFill(
            "solid", fgColor=STATUS_FILLS.get(application.status, "FFFFFF")
        )
        for cell in worksheet[row]:
            cell.border = BORDER
            cell.alignment = Alignment(vertical="top", wrap_text=True)

    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions
    _autosize(worksheet)

    summary = workbook.create_sheet("Ringkasan Statistik")
    summary["A1"] = "Ringkasan Statistik Lamaran"
    summary["A1"].font = TITLE_FONT
    summary.merge_cells("A1:D1")

    summary["A3"] = "Nama Pengguna"
    summary["B3"] = user.full_name
    summary["A4"] = "Tanggal Cetak"
    summary["B4"] = now_wib().strftime("%Y-%m-%d %H:%M WIB")
    summary["A5"] = "Filter"
    summary["B5"] = filter_summary

    summary["A7"] = "Ringkasan Angka"
    summary["A7"].font = SUBTITLE_FONT
    summary.append([])
    summary["A8"] = "Total Lamaran"
    summary["B8"] = kpi.total
    summary["A9"] = "Active Pipeline"
    summary["B9"] = kpi.active_pipeline
    summary["A10"] = "Pernah Interview"
    summary["B10"] = kpi.interview_count
    summary["A11"] = "Interview Rate"
    summary["B11"] = f"{kpi.interview_rate:.1f}%"
    summary["A12"] = "Offering"
    summary["B12"] = kpi.offerings
    summary["A13"] = "Rejected"
    summary["B13"] = kpi.rejected
    summary["A14"] = "Ghosted"
    summary["B14"] = kpi.ghosted

    for row in range(8, 15):
        summary.cell(row=row, column=1).font = Font(bold=True)
        summary.cell(row=row, column=1).border = BORDER
        summary.cell(row=row, column=2).border = BORDER

    status_counts: dict[str, int] = {}
    portal_counts: dict[str, int] = {}
    for application in applications:
        status_counts[application.status] = status_counts.get(application.status, 0) + 1
        portal_counts[application.job_portal] = portal_counts.get(application.job_portal, 0) + 1

    summary["D7"] = "Per Status"
    summary["D7"].font = SUBTITLE_FONT
    summary["D8"] = "Status"
    summary["E8"] = "Jumlah"
    _style_header(summary, 8)
    for offset, (status, count) in enumerate(sorted(status_counts.items()), start=9):
        summary.cell(row=offset, column=4, value=status).border = BORDER
        summary.cell(row=offset, column=5, value=count).border = BORDER

    summary["G7"] = "Per Portal"
    summary["G7"].font = SUBTITLE_FONT
    summary["G8"] = "Portal"
    summary["H8"] = "Jumlah"
    for cell in summary[8][6:8]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = BORDER
    for offset, (portal, count) in enumerate(sorted(portal_counts.items()), start=9):
        summary.cell(row=offset, column=7, value=portal).border = BORDER
        summary.cell(row=offset, column=8, value=count).border = BORDER

    _autosize(summary)

    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()
