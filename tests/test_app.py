import copy

import httpx
import pytest

from src import app as app_module


pytestmark = pytest.mark.anyio

INITIAL_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


@pytest.fixture
async def client():
    transport = httpx.ASGITransport(app=app_module.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client


async def test_get_activities(client):
    response = await client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()


async def test_signup_for_activity(client):
    activity_name = "Chess Club"
    student_email = "test@mergington.edu"

    response = await client.post(f"/activities/{activity_name}/signup?email={student_email}")

    assert response.status_code == 200
    assert student_email in app_module.activities[activity_name]["participants"]


async def test_prevent_duplicate_signup(client):
    activity_name = "Chess Club"
    student_email = "test@mergington.edu"
    await client.post(f"/activities/{activity_name}/signup?email={student_email}")

    response = await client.post(f"/activities/{activity_name}/signup?email={student_email}")

    assert response.status_code == 400


async def test_prevent_signup_when_activity_is_full(client):
    activity_name = "Chess Club"
    app_module.activities[activity_name]["participants"] = [
        f"student{i}@mergington.edu" for i in range(12)
    ]

    response = await client.post(f"/activities/{activity_name}/signup?email=overflow@mergington.edu")

    assert response.status_code == 400
    assert "overflow@mergington.edu" not in app_module.activities[activity_name]["participants"]


async def test_remove_participant_from_activity(client):
    activity_name = "Chess Club"
    student_email = "test@mergington.edu"
    await client.post(f"/activities/{activity_name}/signup?email={student_email}")

    response = await client.delete(f"/activities/{activity_name}/participants?email={student_email}")

    assert response.status_code == 200
    assert student_email not in app_module.activities[activity_name]["participants"]
