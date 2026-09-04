"""Automated End-to-End Pipeline Integration Test.

Simulates the complete FlowKit pipeline flow with mock extension responses:
Project creation -> Video creation -> Scenes creation -> Batch requests -> Queue polling -> Cleanup.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from agent.main import app

client = TestClient(app)


@pytest.fixture
def mock_flow_extension():
    """Mock Chrome extension connection and Flow client API calls."""
    with patch("agent.api.projects.get_flow_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.connected = True

        async def _mock_create_project(name, tool_name="GENERATE"):
            return {
                "data": {
                    "result": {
                        "data": {
                            "json": {
                                "result": {
                                    "projectId": f"mock-flow-p-{uuid.uuid4().hex[:8]}"
                                }
                            }
                        }
                    }
                }
            }

        mock_client.create_project = AsyncMock(side_effect=_mock_create_project)
        mock_get_client.return_value = mock_client
        yield mock_client


def test_e2e_pipeline_workflow(mock_flow_extension):
    # 1. Create a project
    proj_resp = client.post("/api/projects", json={
        "name": "E2E Test Video Project",
        "story": "A heroic journey through the galaxy.",
        "material": "3d_pixar",
        "characters": [{"name": "Hero"}, {"name": "Companion"}],
    })
    assert proj_resp.status_code == 200, proj_resp.text
    proj_data = proj_resp.json()
    project_id = proj_data["id"]
    assert project_id is not None

    # 2. Create a video under the project
    vid_resp = client.post("/api/videos", json={
        "project_id": project_id,
        "title": "Episode 1: Awakening",
        "display_order": 0,
        "orientation": "HORIZONTAL",
    })
    assert vid_resp.status_code == 200, vid_resp.text
    vid_data = vid_resp.json()
    video_id = vid_data["id"]
    assert video_id is not None

    # 3. Create 2 scenes under the video
    scene1_resp = client.post("/api/scenes", json={
        "video_id": video_id,
        "display_order": 0,
        "prompt": "Hero stands on a cliff overlooking futuristic city",
        "video_prompt": "0-3s: Pan right across city. 3-6s: Zoom in on Hero.",
        "narrator_text": "In a universe far away, hope remains.",
        "chain_type": "ROOT",
    })
    assert scene1_resp.status_code == 200, scene1_resp.text
    scene1_id = scene1_resp.json()["id"]

    scene2_resp = client.post("/api/scenes", json={
        "video_id": video_id,
        "parent_scene_id": scene1_id,
        "display_order": 1,
        "prompt": "Companion joins Hero on the cliff",
        "video_prompt": "0-3s: Companion walks up. 3-6s: Both look up at stars.",
        "narrator_text": "Together they embark on the starship.",
        "chain_type": "CONTINUATION",
    })
    assert scene2_resp.status_code == 200, scene2_resp.text
    scene2_id = scene2_resp.json()["id"]

    # 4. Batch submit scene image requests
    batch_resp = client.post("/api/requests/batch", json={
        "requests": [
            {
                "type": "GENERATE_IMAGE",
                "project_id": project_id,
                "video_id": video_id,
                "scene_id": scene1_id,
                "orientation": "HORIZONTAL",
            },
            {
                "type": "GENERATE_IMAGE",
                "project_id": project_id,
                "video_id": video_id,
                "scene_id": scene2_id,
                "orientation": "HORIZONTAL",
            },
        ]
    })
    assert batch_resp.status_code == 200, batch_resp.text
    batch_data = batch_resp.json()
    assert isinstance(batch_data, list)
    assert len(batch_data) == 2

    # 5. Query batch aggregate status
    status_resp = client.get(f"/api/requests/batch-status?video_id={video_id}&type=GENERATE_IMAGE")
    assert status_resp.status_code == 200, status_resp.text
    status_data = status_resp.json()
    assert status_data["total"] == 2
    assert "pending" in status_data

    # 6. Delete project (Cascades to video, scenes, and requests)
    del_resp = client.delete(f"/api/projects/{project_id}")
    assert del_resp.status_code == 200, del_resp.text

    # Verify project is deleted
    get_resp = client.get(f"/api/projects/{project_id}")
    assert get_resp.status_code == 404
