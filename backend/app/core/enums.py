from enum import StrEnum


class ApplicationStatus(StrEnum):
    APPLIED = "Applied"
    SCREENING = "Screening"
    TECHNICAL_TEST = "Technical Test"
    HR_INTERVIEW = "HR Interview"
    USER_INTERVIEW = "User Interview"
    OFFERING = "Offering"
    REJECTED = "Rejected"
    GHOSTED = "Ghosted"


class WorkModel(StrEnum):
    WFO = "WFO"
    HYBRID = "Hybrid"
    REMOTE = "Remote"


class JobPortal(StrEnum):
    LINKEDIN = "LinkedIn"
    GLINTS = "Glints"
    JOBSTREET = "JobStreet"
    KALIBR = "Kalibrr"
    COMPANY_WEBSITE = "Website Perusahaan"
    OTHER = "Lainnya"


INTERVIEW_STAGES: tuple[ApplicationStatus, ...] = (
    ApplicationStatus.HR_INTERVIEW,
    ApplicationStatus.USER_INTERVIEW,
    ApplicationStatus.OFFERING,
)

FOLLOW_UP_STAGES: tuple[ApplicationStatus, ...] = (
    ApplicationStatus.APPLIED,
    ApplicationStatus.SCREENING,
)

ACTIVE_PIPELINE_EXCLUDED: tuple[ApplicationStatus, ...] = (
    ApplicationStatus.REJECTED,
    ApplicationStatus.GHOSTED,
    ApplicationStatus.OFFERING,
)

FOLLOW_UP_DAYS = 14
