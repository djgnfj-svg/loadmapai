"""Tests for roadmap API endpoints."""

import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.roadmap import Roadmap, RoadmapStatus, RoadmapMode


@pytest.fixture
def test_roadmap(db: Session, test_user: User) -> Roadmap:
    """Create a test roadmap."""
    start = date.today()
    roadmap = Roadmap(
        user_id=test_user.id,
        topic="Python 학습",
        title="Python 마스터하기",
        duration_months=3,
        start_date=start,
        end_date=start + timedelta(days=90),  # ~3 months
        mode=RoadmapMode.PLANNING,
        status=RoadmapStatus.ACTIVE,
    )
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)
    return roadmap


class TestListRoadmaps:
    """Test roadmap list endpoint."""

    def test_list_roadmaps_empty(self, authorized_client: TestClient):
        """Test listing roadmaps when none exist."""
        response = authorized_client.get("/api/v1/roadmaps")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_roadmaps_with_data(
        self, authorized_client: TestClient, test_roadmap: Roadmap
    ):
        """Test listing roadmaps with existing data."""
        response = authorized_client.get("/api/v1/roadmaps")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["topic"] == test_roadmap.topic

    def test_list_roadmaps_unauthorized(self, client: TestClient):
        """Test listing roadmaps without authorization."""
        response = client.get("/api/v1/roadmaps")
        assert response.status_code in [401, 403]


class TestCreateRoadmap:
    """Test roadmap creation endpoint."""

    def test_create_roadmap_success(self, authorized_client: TestClient):
        """Test successful roadmap creation."""
        response = authorized_client.post(
            "/api/v1/roadmaps",
            json={
                "topic": "React 학습",
                "duration_months": 2,
                "start_date": str(date.today()),
                "mode": "PLANNING",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["topic"] == "React 학습"
        assert data["duration_months"] == 2
        assert data["mode"] == "PLANNING"

    def test_create_roadmap_invalid_duration(self, authorized_client: TestClient):
        """Test creating roadmap with invalid duration."""
        response = authorized_client.post(
            "/api/v1/roadmaps",
            json={
                "topic": "Test",
                "duration_months": 12,  # Max is 6
                "start_date": str(date.today()),
                "mode": "PLANNING",
            },
        )
        assert response.status_code == 422

    def test_create_roadmap_unauthorized(self, client: TestClient):
        """Test creating roadmap without authorization."""
        response = client.post(
            "/api/v1/roadmaps",
            json={
                "topic": "Test",
                "duration_months": 1,
                "start_date": str(date.today()),
                "mode": "PLANNING",
            },
        )
        assert response.status_code in [401, 403]


class TestGetRoadmap:
    """Test get single roadmap endpoint."""

    def test_get_roadmap_success(
        self, authorized_client: TestClient, test_roadmap: Roadmap
    ):
        """Test getting a roadmap by ID."""
        response = authorized_client.get(f"/api/v1/roadmaps/{test_roadmap.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_roadmap.id)
        assert data["topic"] == test_roadmap.topic

    def test_get_roadmap_not_found(self, authorized_client: TestClient):
        """Test getting non-existent roadmap."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = authorized_client.get(f"/api/v1/roadmaps/{fake_id}")
        assert response.status_code == 404

    def test_get_roadmap_unauthorized(self, client: TestClient, test_roadmap: Roadmap):
        """Test getting roadmap without authorization."""
        response = client.get(f"/api/v1/roadmaps/{test_roadmap.id}")
        assert response.status_code in [401, 403]


class TestUpdateRoadmap:
    """Test roadmap update endpoint."""

    def test_update_roadmap_success(
        self, authorized_client: TestClient, test_roadmap: Roadmap
    ):
        """Test updating a roadmap."""
        response = authorized_client.patch(
            f"/api/v1/roadmaps/{test_roadmap.id}",
            json={"title": "Updated Title"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"

    def test_update_roadmap_status(
        self, authorized_client: TestClient, test_roadmap: Roadmap
    ):
        """Test updating roadmap status."""
        response = authorized_client.patch(
            f"/api/v1/roadmaps/{test_roadmap.id}",
            json={"status": "COMPLETED"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "COMPLETED"


class TestDeleteRoadmap:
    """Test roadmap deletion endpoint."""

    def test_delete_roadmap_success(
        self, authorized_client: TestClient, test_roadmap: Roadmap, db: Session
    ):
        """Test deleting a roadmap."""
        response = authorized_client.delete(f"/api/v1/roadmaps/{test_roadmap.id}")
        assert response.status_code == 204

        # Verify deletion
        response = authorized_client.get(f"/api/v1/roadmaps/{test_roadmap.id}")
        assert response.status_code == 404

    def test_delete_roadmap_not_found(self, authorized_client: TestClient):
        """Test deleting non-existent roadmap."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = authorized_client.delete(f"/api/v1/roadmaps/{fake_id}")
        assert response.status_code == 404
