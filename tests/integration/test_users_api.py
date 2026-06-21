from fastapi.testclient import TestClient


def register(client: TestClient, email: str, name: str) -> None:
    response = client.post(
        "/auth/register",
        json={"email": email, "name": name, "password": "secret123"},
    )
    assert response.status_code == 201, response.text


def token_for(client: TestClient, email: str) -> str:
    response = client.post(
        "/auth/login", data={"username": email, "password": "secret123"}
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def test_list_users_returns_others_excluding_self(client: TestClient) -> None:
    register(client, "ana@example.com", "Ana")
    register(client, "bruno@example.com", "Bruno")
    token = token_for(client, "ana@example.com")

    response = client.get(
        "/users", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
    body = response.json()

    emails = {u["email"] for u in body}
    assert "bruno@example.com" in emails
    assert "ana@example.com" not in emails  # excludes the requester
    assert all("password" not in u for u in body)


def test_list_users_without_token_returns_401(client: TestClient) -> None:
    response = client.get("/users")
    assert response.status_code == 401
