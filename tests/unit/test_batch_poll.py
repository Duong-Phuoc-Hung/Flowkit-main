import pytest
from unittest.mock import patch, MagicMock
from scripts.batch_poll import poll_batch

@patch("scripts.batch_poll.requests.get")
def test_poll_batch_success(mock_get):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "done": True,
        "all_succeeded": True
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    # Call function
    result = poll_batch("video123", "GENERATE_IMAGE", max_retries=1)

    # Assert
    assert result is True
    mock_get.assert_called_once()

@patch("scripts.batch_poll.requests.get")
@patch("scripts.batch_poll.time.sleep", return_value=None) # avoid waiting in tests
def test_poll_batch_fails(mock_sleep, mock_get):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "done": True,
        "all_succeeded": False,
        "failed": 2
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    # Call function
    result = poll_batch("video123", "GENERATE_IMAGE", max_retries=1)

    # Assert
    assert result is False

@patch("scripts.batch_poll.requests.get")
@patch("scripts.batch_poll.time.sleep", return_value=None)
def test_poll_batch_timeout(mock_sleep, mock_get):
    # Setup mock response for network error
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("Network timeout")
    mock_get.return_value = mock_response

    # Call function
    result = poll_batch("video123", "GENERATE_IMAGE", max_retries=2, backoff=0.1)

    # Assert
    assert result is False
    assert mock_get.call_count == 3  # Initial + 2 retries
