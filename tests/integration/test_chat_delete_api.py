from fastapi.testclient import TestClient


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _register(client: TestClient, email: str, name: str) -> None:
    res = client.post(
        "/auth/register",
        json={"email": email, "name": name, "password": "secret123"},
    )
    assert res.status_code == 201, res.text


def _token(client: TestClient, email: str) -> str:
    res = client.post(
        "/auth/login", data={"username": email, "password": "secret123"}
    )
    return res.json()["access_token"]


def test_delete_conversation_clears_it(client: TestClient) -> None:
    _register(client, "ana@example.com", "Ana")
    _register(client, "bruno@example.com", "Bruno")
    ana = _token(client, "ana@example.com")

    users = client.get("/users", headers=_auth(ana)).json()
    bruno_id = next(
        u["id"] for u in users if u["email"] == "bruno@example.com"
    )

    sent = client.post(
        "/chat/messages",
        json={"recipient_id": bruno_id, "content": "oi"},
        headers=_auth(ana),
    )
    assert sent.status_code == 201, sent.text
    assert (
        len(client.get("/chat/conversations", headers=_auth(ana)).json()) == 1
    )

    deleted = client.delete(f"/chat/messages/{bruno_id}", headers=_auth(ana))
    assert deleted.status_code == 204, deleted.text

    assert client.get("/chat/conversations", headers=_auth(ana)).json() == []
    assert (
        client.get(f"/chat/messages/{bruno_id}", headers=_auth(ana)).json()
        == []
    )
