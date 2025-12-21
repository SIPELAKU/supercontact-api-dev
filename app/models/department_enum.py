from enum import StrEnum


class DepartmentEnum(StrEnum):
    MARKETING = "Marketing"
    SALES = "Sales"
    ENGINEERING = "Engineering"
    HUMAN_RESOURCES = "Human Resources"
    CUSTOMER_SUPPORT = "Customer Support"

    @property
    def code(self) -> str:
        return {
            DepartmentEnum.MARKETING: "MAR",
            DepartmentEnum.SALES: "SAL",
            DepartmentEnum.ENGINEERING: "ENG",
            DepartmentEnum.HUMAN_RESOURCES: "HR",
            DepartmentEnum.CUSTOMER_SUPPORT: "CS",
        }[self]
