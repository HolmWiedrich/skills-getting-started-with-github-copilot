"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    global activities
    # Save initial state
    initial_state = {
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
            "description": "Competitive basketball training and interschool matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "lucas@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Learn swimming techniques and participate in swim meets",
            "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["ava@mergington.edu", "mia@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media art techniques",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu", "charlotte@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting workshops and theatrical productions",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["william@mergington.edu", "amelia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking through competitive debates",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["benjamin@mergington.edu", "harper@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Prepare for science competitions and hands-on experiments",
            "schedule": "Fridays, 3:30 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["ethan@mergington.edu", "evelyn@mergington.edu"]
        }
    }
    
    # Reset to initial state
    activities.clear()
    activities.update(initial_state)
    
    yield
    
    # Clean up after test
    activities.clear()
    activities.update(initial_state)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_html(self, client):
        """Test that root path redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_activity_structure(self, client):
        """Test that each activity has the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Signed up newstudent@mergington.edu for Chess Club" in response.json()["message"]
        
        # Verify the student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_duplicate_fails(self, client):
        """Test that signing up twice for the same activity fails"""
        email = "michael@mergington.edu"
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signing up for a non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_multiple_students(self, client):
        """Test signing up multiple students for an activity"""
        students = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        for student in students:
            response = client.post(
                "/activities/Chess Club/signup",
                params={"email": student}
            )
            assert response.status_code == 200
        
        # Verify all students were added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        participants = activities_data["Chess Club"]["participants"]
        
        for student in students:
            assert student in participants


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        email = "michael@mergington.edu"
        
        # Verify student is initially registered
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Chess Club"]["participants"]
        
        # Unregister the student
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        assert f"Unregistered {email} from Chess Club" in response.json()["message"]
        
        # Verify the student was removed
        activities_response = client.get("/activities")
        assert email not in activities_response.json()["Chess Club"]["participants"]
    
    def test_unregister_not_registered_fails(self, client):
        """Test that unregistering a student not in the activity fails"""
        email = "notregistered@mergington.edu"
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()
    
    def test_unregister_nonexistent_activity_fails(self, client):
        """Test that unregistering from a non-existent activity fails"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_and_register_again(self, client):
        """Test that a student can unregister and register again"""
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Unregister
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Register again
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify the student is registered
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity]["participants"]


class TestActivityCapacity:
    """Tests for activity participant capacity"""
    
    def test_activity_has_capacity_info(self, client):
        """Test that activities have max_participants field"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "max_participants" in activity_data
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0


class TestURLEncoding:
    """Tests for URL encoding in activity names"""
    
    def test_signup_with_url_encoded_activity_name(self, client):
        """Test signup with URL-encoded activity name"""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "urltest@mergington.edu"}
        )
        assert response.status_code == 200
    
    def test_unregister_with_url_encoded_activity_name(self, client):
        """Test unregister with URL-encoded activity name"""
        email = "michael@mergington.edu"
        response = client.delete(
            "/activities/Chess%20Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
