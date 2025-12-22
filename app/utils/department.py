import re

DEPARTMENT_CODE_MAP = {
    "marketing": "MAR",
    "human resource": "HR",
    "human resources": "HR",
    "information technology": "IT",
    "finance": "FIN",
    "sales": "SAL",
    "operation": "OPS",
}


def generate_department_code(name: str) -> str:
    key = name.lower().strip()

    # predefined mapping
    if key in DEPARTMENT_CODE_MAP:
        return DEPARTMENT_CODE_MAP[key]

    # fallback otomatis
    # "Customer Support" -> CS
    words = re.findall(r"[A-Za-z]+", key)
    return "".join(word[0] for word in words).upper()
