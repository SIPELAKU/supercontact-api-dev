from app.core import settings

BREVO_URL = "https://api.brevo.com/v3/smtp/email"


def get_brevo_headers():
    return {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json",
    }
