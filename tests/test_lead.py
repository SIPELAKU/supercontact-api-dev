from sqlmodel import select

from app.models import Lead, LeadSource, User, LeadStatus


# TEST GET ALL LEADS
def test_get_all_leads_success(client, auth_token):
    response = client.get(
        "/api/v1/leads",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    response_json = response.json()

    assert "leads" in response_json["data"]
    assert "total" in response_json["data"]
    assert "id" in response_json["data"]["leads"][0]


def test_get_all_leads_without_token(client):
    response = client.get("/api/v1/leads")

    assert response.status_code == 401
    response_json = response.json()

    assert response_json["success"] == False
    assert not response_json["data"]
    assert response_json["error"]["message"] == "Authorization token is required"


def test_get_all_leads_wrong_token(client):
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer Token Salah"}
    )

    assert response.status_code == 401
    response_json = response.json()

    assert response_json["success"] == False
    assert not response_json["data"]
    assert response_json["error"]["message"] == "Invalid access token"


# TEST CREATE NEW LEAD
def test_create_lead_success(client, db_session, auth_token):
    users = db_session.exec(select(User)).all()

    data = {
        "lead_name": "rawrrrrsss ayaya ashiappp",
        "source": LeadSource.WEB_FORM,
        "contact": "string",
        "status": LeadStatus.NEW,
        "assigned_to": str(users[3].id),
        "last_contacted": "2025-11-29"
    }

    response = client.post(
        f"/api/v1/leads",
        json=data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["success"] is True
    assert response_json["data"] is not None
    assert "id" in response_json["data"]


def test_create_lead_failed(client, db_session, auth_token):
    users = db_session.exec(select(User)).all()

    data = {
        "lead_name": "rawrrrrsss ayaya ashiappp",
        "source": "SALAH",
        "contact": "string",
        "status": "SALAH",
        "assigned_to": str(users[3].id),
        "last_contacted": "2025-11-29"
    }

    response = client.post(
        f"/api/v1/leads",
        json=data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 422
    response_json = response.json()

    assert response_json["success"] is False
    assert not response_json["data"]
    assert response_json["error"]["message"] == "Invalid request data"


# TEST GET LEAD BY ID
def test_get_lead_by_id_success(client, db_session, auth_token):
    leads = db_session.exec(select(Lead)).all()

    response = client.get(
        f"/api/v1/leads/{leads[0].id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["success"] is True
    assert response_json["data"] is not None
    assert "id" in response_json["data"]


def test_get_lead_by_wrong_id(client, db_session, auth_token):
    response = client.get(
        f"/api/v1/leads/b96da4b9-0000-0000-0000-e807fafc2872",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 404
    response_json = response.json()

    assert response_json["success"] is False
    assert not response_json["data"]
    assert response_json["error"]["message"] == "Lead not found"


# TEST UPDATE LEAD BY ID
def test_update_lead_by_id_success(client, db_session, auth_token):
    leads = db_session.exec(select(Lead)).all()
    users = db_session.exec(select(User)).all()

    data = {
        "lead_name": "rawrrrrsss ayaya ashiappp",
        "source": LeadSource.WHATSAPP,
        "contact": "string",
        "status": LeadStatus.PROPOSAL,
        "assigned_to": str(users[3].id),
        "last_contacted": "2025-11-29"
    }

    response = client.put(
        f"/api/v1/leads/{leads[0].id}",
        json=data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["success"] is True
    assert response_json["data"] is not None
    assert "id" in response_json["data"]


def test_update_lead_by_wrong_id(client, db_session, auth_token):
    users = db_session.exec(select(User)).all()

    data = {
        "lead_name": "rawrrrrsss ayaya ashiappp",
        "source": LeadSource.WHATSAPP,
        "contact": "string",
        "status": LeadStatus.CONTACTED,
        "assigned_to": str(users[3].id),
        "last_contacted": "2025-11-29"
    }

    response = client.put(
        f"/api/v1/leads/b96da4b9-0000-0000-0000-e807fafc2872",
        json=data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 404
    response_json = response.json()

    assert response_json["success"] is False
    assert not response_json["data"]
    assert response_json["error"]["message"] == "Lead not found"
