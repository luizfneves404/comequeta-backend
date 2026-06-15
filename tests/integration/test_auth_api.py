from fastapi.testclient import TestClient


def register(client: TestClient, **overrides: str) -> None:
    payload = {"email": "ana@example.com", "name": "Ana", "password": "secret123"}
    payload.update(overrides)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201, response.text


def login(client: TestClient, email: str, password: str):
    # OAuth2 password flow sends form data with "username".
    return client.post("/auth/login", data={"username": email, "password": password})


def test_full_auth_flow(client: TestClient) -> None:
    register(client)

    response = login(client, "ana@example.com", "secret123")
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]

    me = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    body = me.json()
    assert body["email"] == "ana@example.com"
    assert body["name"] == "Ana"
    assert "password" not in body and "hashed_password" not in body


def test_register_duplicate_email_returns_409(client: TestClient) -> None:
    register(client)
    response = client.post(
        "/auth/register",
        json={"email": "ana@example.com", "name": "Other", "password": "another12"},
    )
    assert response.status_code == 409


def test_login_with_wrong_password_returns_401(client: TestClient) -> None:
    register(client)
    response = login(client, "ana@example.com", "wrong-password")
    assert response.status_code == 401


def test_me_without_token_returns_401(client: TestClient) -> None:
    response = client.get("/users/me")
    assert response.status_code == 401


def test_me_with_invalid_token_returns_401(client: TestClient) -> None:
    response = client.get("/users/me", headers={"Authorization": "Bearer not-a-valid-token"})
    assert response.status_code == 401
