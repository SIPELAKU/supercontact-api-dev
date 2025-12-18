import httpx

from app.core import settings

BREVO_URL = "https://api.brevo.com/v3/smtp/email"


def get_brevo_headers():
    return {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json",
    }


async def brevo_send_email(payload):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            BREVO_URL,
            headers=get_brevo_headers(),
            json=payload,
        )

    if response.status_code >= 400:
        raise Exception(f"Brevo error: {response.text}")
