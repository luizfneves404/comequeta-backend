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


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_update_location_then_nearby_sees_other_user(
    client: TestClient,
) -> None:
    register(client, "ana@example.com", "Ana")
    register(client, "bruno@example.com", "Bruno")
    ana = token_for(client, "ana@example.com")
    bruno = token_for(client, "bruno@example.com")

    assert (
        client.put(
            "/users/me/location",
            json={"lat": -23.5, "lng": -46.6},
            headers=_auth(ana),
        ).status_code
        == 204
    )
    assert (
        client.put(
            "/users/me/location",
            json={"lat": -23.5001, "lng": -46.6001},
            headers=_auth(bruno),
        ).status_code
        == 204
    )

    res = client.get(
        "/users/nearby",
        params={"lat": -23.5, "lng": -46.6, "radius_m": 500},
        headers=_auth(ana),
    )
    assert res.status_code == 200, res.text
    body = res.json()
    names = {u["name"] for u in body}
    assert "Bruno" in names  # nearby
    assert "Ana" not in names  # excludes self
    assert all("lat" in u and "lng" in u for u in body)


def test_nearby_excludes_far_and_locationless_users(
    client: TestClient,
) -> None:
    register(client, "ana@example.com", "Ana")
    register(client, "far@example.com", "Far")
    register(client, "noloc@example.com", "NoLoc")
    ana = token_for(client, "ana@example.com")
    far = token_for(client, "far@example.com")

    client.put(
        "/users/me/location",
        json={"lat": -23.5, "lng": -46.6},
        headers=_auth(ana),
    )
    # ~50 km away.
    client.put(
        "/users/me/location",
        json={"lat": -23.9, "lng": -46.9},
        headers=_auth(far),
    )
    # "NoLoc" never reports a location.

    res = client.get(
        "/users/nearby",
        params={"lat": -23.5, "lng": -46.6, "radius_m": 500},
        headers=_auth(ana),
    )
    assert res.status_code == 200
    assert res.json() == []
