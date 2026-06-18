import copy

from fastapi.testclient import TestClient
import pytest

from src import app as app_module

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = original_activities


def test_get_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"


def test_signup_and_activity_update():
    email = "teststudent@mergington.edu"
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    assert response.status_code == 200
    assert email in client.get("/activities").json()["Chess Club"]["participants"]
    assert "Signed up" in response.json()["message"]


def test_signup_existing_participant():
    response = client.post(
        "/activities/Chess%20Club/signup", params={"email": "michael@mergington.edu"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant():
    email = "noah@mergington.edu"
    response = client.delete(f"/activities/Soccer%20Team/participants/{email}")

    assert response.status_code == 200
    assert email not in client.get("/activities").json()["Soccer Team"]["participants"]
    assert response.json()["message"] == f"Removed {email} from Soccer Team"


def test_remove_nonexistent_participant():
    response = client.delete(
        "/activities/Chess%20Club/participants/nonexistent@mergington.edu"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Participant not found in this activity"


def test_signup_with_special_characters():
    # email with dot and plus sign (commonly used aliases)
    email = "user.name+alias@mergington.edu"
    response = client.post("/activities/Programming%20Class/signup", params={"email": email})

    assert response.status_code == 200
    data = client.get("/activities").json()
    assert email in data["Programming Class"]["participants"]
    assert "Signed up" in response.json()["message"]
