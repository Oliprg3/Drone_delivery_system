"""Tests for the HTTP API. Skipped when the optional api extras are missing."""

from __future__ import annotations

import pytest

from drone_delivery.services.simulation import Simulation

pytest.importorskip("fastapi", reason="the api extra is not installed")

fastapi_testclient = pytest.importorskip(
    "fastapi.testclient", reason="fastapi is installed without test support"
)
pytest.importorskip("httpx", reason="httpx is required by the fastapi test client")

TestClient = fastapi_testclient.TestClient


@pytest.fixture
def client():
    from drone_delivery.api.server import create_app

    with TestClient(create_app(Simulation())) as test_client:
        yield test_client


def test_health_reports_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_state_lists_the_fleet(client):
    response = client.get("/state")

    assert response.status_code == 200
    body = response.json()
    assert len(body["drones"]) == 3
    assert body["step"] == 0


def test_posting_an_order_adds_it(client):
    response = client.post("/order", json={"pickup": [1, 1], "delivery": [4, 4]})

    assert response.status_code == 201
    assert response.json()["status"] == "added"
    assert client.get("/state").json()["orders"]


def test_posting_an_order_on_a_blocked_cell_is_rejected(client):
    response = client.post("/order", json={"pickup": [999, 999], "delivery": [4, 4]})

    assert response.status_code == 422


def test_step_advances_the_simulation(client):
    response = client.post("/step")

    assert response.status_code == 200
    assert response.json()["step"] == 1


def test_reset_restores_the_initial_state(client):
    client.post("/step")
    client.post("/reset")

    assert client.get("/state").json()["step"] == 0


def test_metrics_endpoint_serves_prometheus_text(client):
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "drone_active_orders" in response.text
