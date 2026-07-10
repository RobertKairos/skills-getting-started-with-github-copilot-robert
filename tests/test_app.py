from fastapi.testclient import TestClient

from src import app as app_module


client = TestClient(app_module.app)


def test_remove_participant_from_activity():
    app_module.activities["Chess Club"]["participants"] = ["michael@mergington.edu", "daniel@mergington.edu"]

    signup_response = client.post(
        "/activities/Chess Club/signup?email=student@mergington.edu"
    )
    assert signup_response.status_code == 200

    remove_response = client.delete(
        "/activities/Chess Club/participants?email=student@mergington.edu"
    )

    assert remove_response.status_code == 200
    assert "student@mergington.edu" not in app_module.activities["Chess Club"]["participants"]
