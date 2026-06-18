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
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"


def test_signup_and_activity_update():
    # Arrange
    email = "teststudent@mergington.edu"
    url = "/activities/Chess%20Club/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]
    assert "Signed up" in response.json()["message"]


def test_signup_existing_participant():
    # Arrange
    url = "/activities/Chess%20Club/signup"
    email = "michael@mergington.edu"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant():
    # Arrange
    email = "noah@mergington.edu"
    url = f"/activities/Soccer%20Team/participants/{email}"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 200
    activities = client.get("/activities").json()
    assert email not in activities["Soccer Team"]["participants"]
    assert response.json()["message"] == f"Removed {email} from Soccer Team"


def test_remove_nonexistent_participant():
    # Arrange
    url = "/activities/Chess%20Club/participants/nonexistent@mergington.edu"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Participant not found in this activity"


def test_signup_with_special_characters():
    # Arrange
    email = "user.name+alias@mergington.edu"
    url = "/activities/Programming%20Class/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    data = client.get("/activities").json()
    assert email in data["Programming Class"]["participants"]
    assert "Signed up" in response.json()["message"]


def test_signup_with_special_characters():
    # email with dot and plus sign (commonly used aliases)
    email = "user.name+alias@mergington.edu"
    response = client.post("/activities/Programming%20Class/signup", params={"email": email})

    assert response.status_code == 200
    data = client.get("/activities").json()
    assert email in data["Programming Class"]["participants"]
    assert "Signed up" in response.json()["message"]
