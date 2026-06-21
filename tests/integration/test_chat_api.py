from fastapi.testclient import TestClient


def register_and_login(
    client: TestClient, email: str, name: str
) -> tuple[int, str]:
    client.post(
        "/auth/register",
        json={"email": email, "name": name, "password": "secret123"},
    )
    login = client.post(
        "/auth/login", data={"username": email, "password": "secret123"}
    )
    token = login.json()["access_token"]
    me = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    return me.json()["id"], token


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_send_message_persists_and_appears_in_history(
    client: TestClient,
) -> None:
    _ana_id, ana = register_and_login(client, "ana@x.com", "Ana")
    bia_id, bia = register_and_login(client, "bia@x.com", "Bia")

    response = client.post(
        "/chat/messages",
        json={"recipient_id": bia_id, "content": "ola"},
        headers=auth(ana),
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["content"] == "ola"
    assert body["recipient_id"] == bia_id

    history = client.get(f"/chat/messages/{bia_id}", headers=auth(ana))
    assert history.status_code == 200
    assert [m["content"] for m in history.json()] == ["ola"]

    # Bia sees the same conversation from her side.
    bia_history = client.get(f"/chat/messages/{_ana_id}", headers=auth(bia))
    assert [m["content"] for m in bia_history.json()] == ["ola"]


def test_send_to_unknown_recipient_returns_404(client: TestClient) -> None:
    _ana_id, ana = register_and_login(client, "ana@x.com", "Ana")
    response = client.post(
        "/chat/messages",
        json={"recipient_id": 9999, "content": "ola"},
        headers=auth(ana),
    )
    assert response.status_code == 404


def test_conversations_summary_with_unread(client: TestClient) -> None:
    ana_id, ana = register_and_login(client, "ana@x.com", "Ana")
    bia_id, bia = register_and_login(client, "bia@x.com", "Bia")

    client.post(
        "/chat/messages",
        json={"recipient_id": ana_id, "content": "oi"},
        headers=auth(bia),
    )
    client.post(
        "/chat/messages",
        json={"recipient_id": ana_id, "content": "tudo bem?"},
        headers=auth(bia),
    )

    convos = client.get("/chat/conversations", headers=auth(ana))
    assert convos.status_code == 200
    data = convos.json()
    assert len(data) == 1
    assert data[0]["peer_id"] == bia_id
    assert data[0]["peer_name"] == "Bia"
    assert data[0]["last_message"] == "tudo bem?"
    assert data[0]["unread"] == 2


def test_mark_read_clears_unread(client: TestClient) -> None:
    ana_id, ana = register_and_login(client, "ana@x.com", "Ana")
    bia_id, bia = register_and_login(client, "bia@x.com", "Bia")

    client.post(
        "/chat/messages",
        json={"recipient_id": ana_id, "content": "oi"},
        headers=auth(bia),
    )

    read = client.post(f"/chat/messages/{bia_id}/read", headers=auth(ana))
    assert read.status_code == 204

    convos = client.get("/chat/conversations", headers=auth(ana)).json()
    assert convos[0]["unread"] == 0


def test_chat_requires_auth(client: TestClient) -> None:
    assert client.get("/chat/conversations").status_code == 401
    assert client.get("/chat/messages/1").status_code == 401
    assert (
        client.post(
            "/chat/messages", json={"recipient_id": 1, "content": "x"}
        ).status_code
        == 401
    )


def test_websocket_delivers_message(client: TestClient) -> None:
    ana_id, ana = register_and_login(client, "ana@x.com", "Ana")
    bia_id, bia = register_and_login(client, "bia@x.com", "Bia")

    with client.websocket_connect(f"/ws/chat?token={bia}") as bia_ws:
        # Ana sends to Bia via REST; Bia's socket should receive it.
        client.post(
            "/chat/messages",
            json={"recipient_id": bia_id, "content": "via rest"},
            headers=auth(ana),
        )
        frame = bia_ws.receive_json()
        assert frame["type"] == "message"
        assert frame["message"]["content"] == "via rest"
        assert frame["message"]["sender_id"] == ana_id


def test_websocket_inbound_frame_routes_and_echoes(
    client: TestClient,
) -> None:
    ana_id, ana = register_and_login(client, "ana@x.com", "Ana")
    bia_id, bia = register_and_login(client, "bia@x.com", "Bia")

    with (
        client.websocket_connect(f"/ws/chat?token={ana}") as ana_ws,
        client.websocket_connect(f"/ws/chat?token={bia}") as bia_ws,
    ):
        ana_ws.send_json(
            {
                "type": "message",
                "recipient_id": bia_id,
                "content": "ws hello",
            }
        )
        # Echo back to the sender.
        echo = ana_ws.receive_json()
        assert echo["message"]["content"] == "ws hello"
        # Delivered to the recipient.
        delivered = bia_ws.receive_json()
        assert delivered["message"]["content"] == "ws hello"
        assert delivered["message"]["sender_id"] == ana_id
        assert delivered["message"]["recipient_id"] == bia_id


def test_websocket_rejects_invalid_token(client: TestClient) -> None:
    import pytest
    from starlette.websockets import WebSocketDisconnect

    with (
        pytest.raises(WebSocketDisconnect),
        client.websocket_connect("/ws/chat?token=not-valid") as ws,
    ):
        ws.receive_json()
