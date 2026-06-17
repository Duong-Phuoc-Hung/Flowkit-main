import json
import logging
import os
import time
from typing import Any, Dict, Optional
import requests
SETTINGS = {
    'CONFIG_DIR': './config',
    'MAX_RETRIES': 3,
    'REQUEST_TIMEOUT': 30
}

logger = logging.getLogger(__name__)

# Load API keys from config/api_keys.txt (or env var) – rotate when needed
_API_KEYS = []
_current_key_idx = 0

def _load_api_keys() -> None:
    global _API_KEYS, _current_key_idx
    env_key = os.getenv('FLOWKIT_API_KEY')
    if env_key:
        _API_KEYS = [env_key]
    else:
        api_keys_path = os.path.join(SETTINGS['CONFIG_DIR'], 'api_keys.txt')
        if os.path.exists(api_keys_path):
            with open(api_keys_path, 'r', encoding='utf-8') as f:
                _API_KEYS = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    _current_key_idx = 0
    if not _API_KEYS:
        logger.warning('No API keys found for Gemini. Functions that require Gemini will fail.')

_load_api_keys()

def _current_key() -> Optional[str]:
    if _API_KEYS:
        return _API_KEYS[_current_key_idx]
    return None

def _rotate_key() -> None:
    global _current_key_idx
    if len(_API_KEYS) > 1:
        _current_key_idx = (_current_key_idx + 1) % len(_API_KEYS)
        logger.info(f'Rotated to API key #{_current_key_idx + 1}')
    else:
        logger.warning('Only one API key available; cannot rotate.')

def _request(method: str, url: str, **kwargs) -> requests.Response:
    """Internal request with retry, timeout, and key rotation for Gemini endpoints.
    """
    max_retries = SETTINGS.get('MAX_RETRIES', 3)
    timeout = SETTINGS.get('REQUEST_TIMEOUT', 30)
    for attempt in range(1, max_retries + 1):
        try:
            # Inject Gemini API key if the request is to the Gemini endpoint
            if 'generative' in url.lower() or 'google' in url.lower():
                key = _current_key()
                if key:
                    headers = kwargs.pop('headers', {})
                    headers['x-goog-api-key'] = key
                    kwargs['headers'] = headers
            response = requests.request(method, url, timeout=timeout, **kwargs)
            if response.status_code == 429 or response.status_code == 403:
                # Quota exceeded or key invalid – rotate if possible
                logger.warning(f'Quota/Key issue on attempt {attempt} for {url}: {response.status_code}')
                _rotate_key()
                time.sleep(2 ** attempt)  # exponential backoff
                continue
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f'Request error on attempt {attempt} for {url}: {e}')
            if attempt == max_retries:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError('Unexpected exit from _request')

def get(url: str, **kwargs) -> requests.Response:
    return _request('GET', url, **kwargs)

def post(url: str, json: Optional[Dict[str, Any]] = None, data: Optional[Any] = None, **kwargs) -> requests.Response:
    return _request('POST', url, json=json, data=data, **kwargs)

def patch(url: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
    return _request('PATCH', url, json=json, **kwargs)
