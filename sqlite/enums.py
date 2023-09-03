import enum


class DepartmentsEnum(str, enum.Enum):
    ELECTRONICS = "electronics"
    COMPUTER_SCIENCE = "computer_science"
    SOFTWATE = "software"
    TELECOM = "telecom"
    BIOMEDICAL = "biomedical"


class DesignationsEnum(str, enum.Enum):
    JUNIOR_LECTURER = "junior_lecturer"
    LECTURER = "lecturer"
    ASSISTANT_PROFESSOR = "assistant_professor"
    ASSOCIATE_PROFESSOR = "associate_professor"
    PROFESSOR = "professor"
    VISITING = "visiting"
    CHAIRMAN = "chairman"
