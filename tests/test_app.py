import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Original activities data for resetting
ORIGINAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Join the competitive basketball team and compete in tournaments",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["alex@mergington.edu"]
    },
    "Tennis Club": {
        "description": "Learn and practice tennis skills with other students",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 10,
        "participants": []
    },
    "Art Studio": {
        "description": "Create paintings, drawings, and other visual artworks",
        "schedule": "Mondays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["maya@mergington.edu"]
    },
    "Music Band": {
        "description": "Play musical instruments and perform in school concerts",
        "schedule": "Wednesdays and Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 25,
        "participants": ["lucas@mergington.edu", "isabella@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills through competitive debates",
        "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["jordan@mergington.edu"]
    },
    "Science Club": {
        "description": "Explore scientific concepts through experiments and projects",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["alex@mergington.edu", "casey@mergington.edu"]
    }
}


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app, follow_redirects=False)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities dictionary before each test."""
    activities.clear()
    activities.update(ORIGINAL_ACTIVITIES)


def test_root_redirect(client):
    """Test that root endpoint redirects to static/index.html."""
    response = client.get("/")
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test getting all activities."""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # 9 activities
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Check structure of one activity
    chess = data["Chess Club"]
    assert "description" in chess
    assert "schedule" in chess
    assert "max_participants" in chess
    assert "participants" in chess
    assert isinstance(chess["participants"], list)


def test_signup_successful(client):
    """Test successful signup for an activity."""
    response = client.post("/activities/Tennis Club/signup?email=test@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Signed up test@mergington.edu for Tennis Club" in data["message"]
    # Verify the participant was added
    get_response = client.get("/activities")
    activities_data = get_response.json()
    assert "test@mergington.edu" in activities_data["Tennis Club"]["participants"]


def test_signup_already_enrolled(client):
    """Test signup when student is already enrolled."""
    # First signup
    client.post("/activities/Tennis Club/signup?email=test@mergington.edu")
    # Try again
    response = client.post("/activities/Tennis Club/signup?email=test@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student is already signed up for this activity" in data["detail"]


def test_signup_activity_not_found(client):
    """Test signup for non-existent activity."""
    response = client.post("/activities/NonExistent Activity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_remove_participant_successful(client):
    """Test successful removal of a participant."""
    # First add a participant
    client.post("/activities/Tennis Club/signup?email=test@mergington.edu")
    # Now remove
    response = client.delete("/activities/Tennis Club/participants/test@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Removed test@mergington.edu from Tennis Club" in data["message"]
    # Verify removed
    get_response = client.get("/activities")
    activities_data = get_response.json()
    assert "test@mergington.edu" not in activities_data["Tennis Club"]["participants"]


def test_remove_participant_activity_not_found(client):
    """Test removal from non-existent activity."""
    response = client.delete("/activities/NonExistent Activity/participants/test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_remove_participant_not_enrolled(client):
    """Test removal when student is not enrolled."""
    response = client.delete("/activities/Tennis Club/participants/notenrolled@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Student is not signed up for this activity" in data["detail"]