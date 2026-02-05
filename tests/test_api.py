"""Tests for the Mergington High School Activities API"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    global activities
    activities.clear()
    activities.update({
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
            "description": "Competitive basketball training and games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis lessons and friendly matches",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 10,
            "participants": ["lucas@mergington.edu", "grace@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theatrical productions and acting workshops",
            "schedule": "Wednesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["isabella@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and mixed media creation",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["mia@mergington.edu", "noah@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debate and public speaking",
            "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["james@mergington.edu"]
        },
        "Science Club": {
            "description": "Experiments, research projects, and STEM exploration",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["amelia@mergington.edu", "ethan@mergington.edu"]
        }
    })
    yield
    # Cleanup after test


class TestActivitiesEndpoint:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_contains_correct_structure(self, client, reset_activities):
        """Test that activity data has correct structure"""
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_contains_participants(self, client, reset_activities):
        """Test that activities include their participants"""
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]

    def test_signup_duplicate_email_rejected(self, client, reset_activities):
        """Test that duplicate signup is rejected"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test that signup for nonexistent activity fails"""
        response = client.post(
            "/activities/Fake%20Activity/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """Test that signup correctly adds participant"""
        initial_count = len(activities["Programming Class"]["participants"])
        response = client.post(
            "/activities/Programming%20Class/signup?email=luke@mergington.edu"
        )
        assert response.status_code == 200
        assert len(activities["Programming Class"]["participants"]) == initial_count + 1
        assert "luke@mergington.edu" in activities["Programming Class"]["participants"]

    def test_signup_with_special_characters_in_email(self, client, reset_activities):
        """Test signup with complex email addresses"""
        response = client.post(
            "/activities/Art%20Studio/signup?email=student.name%2B1@mergington.edu"
        )
        assert response.status_code == 200
        assert "student.name+1@mergington.edu" in activities["Art Studio"]["participants"]


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/participants endpoint"""

    def test_unregister_successful(self, client, reset_activities):
        """Test successful unregister from an activity"""
        response = client.delete(
            "/activities/Chess%20Club/participants?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]

    def test_unregister_nonexistent_participant(self, client, reset_activities):
        """Test that unregister for nonexistent participant fails"""
        response = client.delete(
            "/activities/Chess%20Club/participants?email=notexist@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test that unregister from nonexistent activity fails"""
        response = client.delete(
            "/activities/Fake%20Activity/participants?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister correctly removes participant"""
        initial_count = len(activities["Gym Class"]["participants"])
        response = client.delete(
            "/activities/Gym%20Class/participants?email=john@mergington.edu"
        )
        assert response.status_code == 200
        assert len(activities["Gym Class"]["participants"]) == initial_count - 1
        assert "john@mergington.edu" not in activities["Gym Class"]["participants"]

    def test_unregister_then_signup_again(self, client, reset_activities):
        """Test that a participant can unregister and sign up again"""
        # Unregister
        response1 = client.delete(
            "/activities/Tennis%20Club/participants?email=lucas@mergington.edu"
        )
        assert response1.status_code == 200
        assert "lucas@mergington.edu" not in activities["Tennis Club"]["participants"]

        # Sign up again
        response2 = client.post(
            "/activities/Tennis%20Club/signup?email=lucas@mergington.edu"
        )
        assert response2.status_code == 200
        assert "lucas@mergington.edu" in activities["Tennis Club"]["participants"]


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static(self, client):
        """Test that root redirects to static HTML"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert "/static/index.html" in response.headers["location"]
