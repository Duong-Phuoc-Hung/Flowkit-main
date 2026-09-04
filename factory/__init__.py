"""factory/ — Auto Factory Pipeline Stages

Splits the 566-line auto_factory.py monolith into focused stage modules.
Each module handles one pipeline stage and exposes a single entry function.

Usage:
    from factory import run_pipeline
    run_pipeline()

Stage order:
    1. stage_script   — AI script generation (Gemini)
    2. stage_images   — Reference + scene image generation
    3. stage_videos   — AI video rendering
    4. stage_concat   — ffmpeg concat + BGM mixing
    5. stage_upload   — YouTube upload
"""

from factory._shared import FactoryConfig, update_status, is_night_mode_active  # noqa: F401
