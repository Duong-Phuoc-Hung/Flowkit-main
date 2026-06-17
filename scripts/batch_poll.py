"""batch_poll.py – Helper to poll FlowKit batch API until all requests are completed.

Usage example:
    from batch_poll import poll_batch
    poll_batch(video_id='abcd1234', request_type='GENERATE_IMAGE')
"""
import os
import time
import json
import warnings
import requests

warnings.filterwarnings("ignore", category=FutureWarning)

BASE_URL = os.getenv("FLOWKIT_BASE_URL", "http://127.0.0.1:8100")

def poll_batch(target_id: str, request_type: str, max_retries: int = 3, backoff: float = 5.0):
    """Poll the batch‑status endpoint until `done` is true.

    Parameters
    ----------
    target_id: str
        The video ID or project ID used in the original batch request.
    request_type: str
        The request type, e.g. ``GENERATE_IMAGE`` or ``GENERATE_VIDEO``.
    max_retries: int
        Number of times to retry after a failure or non‑successful status.
    backoff: float
        Initial back‑off seconds; will double on each retry.
    """
    endpoint = f"{BASE_URL}/api/requests/batch-status"
    
    params = {"type": request_type}
    if request_type == "GENERATE_CHARACTER_IMAGE":
        params["project_id"] = target_id
    else:
        params["video_id"] = target_id
    attempt = 0
    while attempt <= max_retries:
        try:
            resp = requests.get(endpoint, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            if data.get("done"):
                if data.get("all_succeeded"):
                    print(f"✅ All {request_type} requests for target {target_id} succeeded.")
                    return True
                else:
                    print(f"⚠️ Batch completed but some requests failed: {data}")
                    return False
            else:
                print(f"⏳ Waiting – {data.get('pending',0)} pending, {data.get('processing',0)} processing…")
                time.sleep(10)
                # Reset error attempt counter when we get a valid "still processing" response
                attempt = 0
                continue
        except Exception as e:
            print(f"❌ Error polling batch status: {e}")
            attempt += 1
            sleep_time = backoff * (2 ** (attempt - 1))
            print(f"⏱️ Sleeping {sleep_time}s before next poll (attempt {attempt}/{max_retries})")
            time.sleep(sleep_time)
    print("🚨 Max retries exceeded (Network/Server errors) – aborting poll.")
    return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Poll FlowKit batch status until done.")
    parser.add_argument("target_id", help="Video ID or Project ID used in batch request")
    parser.add_argument("request_type", help="Request type, e.g. GENERATE_IMAGE or GENERATE_CHARACTER_IMAGE")
    args = parser.parse_args()
    poll_batch(args.target_id, args.request_type)
