from enum import Enum


class UserPosition(str, Enum):
    BUSINESS_OWNER = "Business Owner"
    C_LEVEL = "C-Level"
    SENIOR_MANAGER = "Senior Manager"
    STAFF = "Staff"
    OTHER = "Lainnya"
