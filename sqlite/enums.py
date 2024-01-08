import enum


class DepartmentsEnum(str, enum.Enum):
    NOT_SPECIFIED = "not_specified"
    BIOMEDICAL = "biomedical"
    COMPUTER_SCIENCE = "computer_science"
    ELECTRONICS = "electronics"
    SOFTWATE = "software"
    TELECOM = "telecom"


class DesignationsEnum(str, enum.Enum):
    NOT_SPECIFIED = "not_specified"
    CHAIRMAN = "chairman"
    PROFESSOR = "professor"
    ASSOCIATE_PROFESSOR = "associate_professor"
    ASSISTANT_PROFESSOR = "assistant_professor"
    LECTURER = "lecturer"
    JUNIOR_LECTURER = "junior_lecturer"
    VISITING = "visiting"


class DaysEnum(str, enum.Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class AttendanceEnum(str, enum.Enum):
    PRESENT = "present"
    LATE = "late"
