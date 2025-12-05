import pytest
from sqlmodel import select

from app.models import Lead, LeadSource, User, LeadStatus

lead_prefix = "/api/v1/leads"


async def get_all(db_async_session, table):
    result = await db_async_session.scalars(select(table))
    return result.all()


# TEST GET ALL LEADS
@pytest.mark.asyncio
async def test_get_all_leads_success(client, auth_token):
    response = await client.get(
        lead_prefix,
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    response_json = response.json()

    assert "leads" in response_json["data"]
    assert "total" in response_json["data"]
    assert "id" in response_json["data"]["leads"][0]


@pytest.mark.asyncio
async def test_get_all_leads_without_token(client):
    response = await client.get(lead_prefix)

    assert response.status_code == 401
    response_json = response.json()

    assert response_json["success"] == False
    assert not response_json["data"]
    assert response_json["error"]["message"] == "Authorization token is required"


@pytest.mark.asyncio
async def test_get_all_leads_wrong_token(client):
    response = await client.get(
        lead_prefix,
        headers={"Authorization": f"Bearer Token Salah"}
    )

    assert response.status_code == 401
    response_json = response.json()

    assert response_json["success"] == False
    assert not response_json["data"]
    assert response_json["error"]["message"] == "Invalid access token"


# TEST CREATE NEW LEAD
@pytest.mark.asyncio
async def test_create_lead_success(client, db_async_session, auth_token):
    users = await get_all(db_async_session, User)

    data = {
        "lead_name": "rawrrrrsss ayaya ashiappp",
        "source": LeadSource.WEB_FORM,
        "contact": "string",
        "status": LeadStatus.NEW,
        "assigned_to": str(users[3].id),
        "last_contacted": "2025-11-29"
    }

    response = await client.post(
        lead_prefix,
        json=data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["success"] is True
    assert response_json["data"] is not None
    assert "id" in response_json["data"]


@pytest.mark.asyncio
async def test_create_lead_failed(client, db_async_session, auth_token):
    users = await get_all(db_async_session, User)

    data = {
        "lead_name": "rawrrrrsss ayaya ashiappp",
        "source": "SALAH",
        "contact": "string",
        "status": "SALAH",
        "assigned_to": str(users[3].id),
        "last_contacted": "2025-11-29"
    }

    response = await client.post(
        lead_prefix,
        json=data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 422
    response_json = response.json()

    assert response_json["success"] is False
    assert not response_json["data"]
    assert response_json["error"]["message"] == "Invalid request data"


# TEST GET LEAD BY ID
@pytest.mark.asyncio
async def test_get_lead_by_id_success(client, db_async_session, auth_token):
    leads = await get_all(db_async_session, Lead)

    response = await client.get(
        f"{lead_prefix}/{leads[0].id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["success"] is True
    assert response_json["data"] is not None
    assert "id" in response_json["data"]


@pytest.mark.asyncio
async def test_get_lead_by_wrong_id(client, auth_token):
    response = await client.get(
        f"{lead_prefix}/b96da4b9-0000-0000-0000-e807fafc2872",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 404
    response_json = response.json()

    assert response_json["success"] is False
    assert not response_json["data"]
    assert response_json["error"]["message"] == "Lead not found"


# TEST UPDATE LEAD BY ID
@pytest.mark.asyncio
async def test_update_lead_by_id_success(client, db_async_session, auth_token):
    leads = await get_all(db_async_session, Lead)
    users = await get_all(db_async_session, User)

    data = {
        "lead_name": "rawrrrrsss ayaya ashiappp",
        "source": LeadSource.WHATSAPP,
        "contact": "string",
        "status": LeadStatus.PROPOSAL,
        "assigned_to": str(users[3].id),
        "last_contacted": "2025-11-29"
    }

    response = await client.put(
        f"{lead_prefix}/{leads[0].id}",
        json=data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["success"] is True
    assert response_json["data"] is not None
    assert "id" in response_json["data"]


@pytest.mark.asyncio
async def test_update_lead_by_wrong_id(client, db_async_session, auth_token):
    users = await get_all(db_async_session, User)

    data = {
        "lead_name": "rawrrrrsss ayaya ashiappp",
        "source": LeadSource.WHATSAPP,
        "contact": "string",
        "status": LeadStatus.CONTACTED,
        "assigned_to": str(users[3].id),
        "last_contacted": "2025-11-29"
    }

    response = await client.put(
        f"{lead_prefix}/b96da4b9-0000-0000-0000-e807fafc2872",
        json=data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 404
    response_json = response.json()

    assert response_json["success"] is False
    assert not response_json["data"]
    assert response_json["error"]["message"] == "Lead not found"
