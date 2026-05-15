from enum import StrEnum


class DepartmentDeleteMode(StrEnum):
    CASCADE = "cascade"
    REASSIGN = "reassign"
