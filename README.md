# FLOW KIT

<div align="center">

**AI Video Production System — From Idea to YouTube, Fully Automated**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Chrome](https://img.shields.io/badge/Chrome_Extension-MV3-4285F4?logo=googlechrome&logoColor=white)](extension/)
[![ffmpeg](https://img.shields.io/badge/ffmpeg-required-007808?logo=ffmpeg&logoColor=white)](https://ffmpeg.org)

[Quick Start](#quick-start) . [Architecture](#architecture) . [Skills](#ai-skills) . [API](#api-reference) . [Community](#community)

</div>

---

## Overview

FlowKit is a complete AI video production pipeline that automates everything from story generation to YouTube publishing, powered by **Google Flow API**, orchestrated through a local Python agent and Chrome extension bridge.

`
Story Idea  ->  Script (AI)  ->  Reference Images  ->  Scene Images
    ->  AI Videos (8s clips)  ->  Concat + BGM  ->  YouTube Upload
`

---

## Architecture

`
+-----------------------------+         +------------------------------+
|        Python Agent         |<--WS--->|      Chrome Extension        |
|      FastAPI + SQLite       |  :9222  |      MV3 Service Worker      |
|                             |         |                              |
|  REST API          :8100    |         |  Capture token  ya29.*       |
|  Queue Worker   (5 conc.)   |         |  Solve reCAPTCHA v2          |
|  SQLite DB                  |         |  Proxy Google Flow API       |
|  Post-process   (ffmpeg)    |         |  Live Dashboard UI           |
+-------------+---------------+         +------------------------------+
              |
              v
+-----------------------------+         +------------------------------+
|    Auto Factory Pipeline    |<-HTTP-->|      Web Dashboard           |
|                             |  :3000  |      Next.js 15              |
|  Stage 1  Script (Gemini)   |         |                              |
|  Stage 2  Images            |         |  Station 1  Input Idea       |
|  Stage 3  Videos            |         |  Station 2  Review Script    |
|  Stage 4  Concat + BGM      |         |  Station 3  Render Monitor   |
|  Stage 5  YouTube Upload    |         |  Station 4  Final Output     |
+-----------------------------+         |  Station 5  YouTube Upload   |
                                        +------------------------------+
`

---

## Components

### Python Agent (gent/)

Core backend that manages the entire pipeline.

| Module | Description |
|--------|-------------|
| gent/main.py | FastAPI app + WebSocket server |
| gent/worker/ | Queue processor (max 5 concurrent, 10s cooldown) |
| gent/sdk/ | Domain SDK: Project, Video, Scene, Character |
| gent/api/ | REST routes for all resources |
| gent/services/ | FlowClient bridge, headers, post-processing |
| gent/db/ | SQLite schema + async CRUD (aiosqlite) |

### Chrome Extension (extension/)

Browser bridge between the agent and Google Flow.

| File | Description |
|------|-------------|
| ackground.js | WebSocket server + token capture (ya29.*) |
| content.js | reCAPTCHA v2 auto-solver |
| popup.html/js | Live dashboard: request log, progress, status |

### Auto Factory (actory/)

5-stage automated production pipeline.

| Stage | File | What It Does |
|-------|------|--------------|
| 1 | stage_1_script.py | Generate full video script using Gemini AI |
| 2 | stage_2_images.py | Generate reference images + scene images |
| 3 | stage_3_videos.py | Render AI videos (8s per scene) |
| 4 | stage_4_concat.py | ffmpeg concat + background music mix |
| 5 | stage_5_upload.py | Automated YouTube upload with scheduling |

### Web Dashboard (lowkit-web/)

Next.js 15 control panel organized as pipeline stations.

| Route | Station | Function |
|-------|---------|----------|
| / | Station 1 | Submit story idea, name project |
| /tram-2 | Station 2 | Review and edit AI-generated script |
| /tram-2-5 | Station 2.5 | Approve reference images |
| /tram-3 | Station 3 | Monitor scene image rendering |
| /diep-vien | Agents | Manage characters and entities |
| /tram-4 | Station 4 | Preview final video output |
| /tram-5 | Station 5 | YouTube upload and publish |
| /ai-phan-tich | AI Analysis | AI-powered video quality analysis |
| /cau-hinh | Config | System settings |

---

## Quick Start

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.10+ | Required |
| Node.js | 18+ | Web dashboard only |
| Google Chrome | Latest | Required |
| ffmpeg | Any | See Step 1 |

### Step 1 — Install ffmpeg

`ash
# Auto-detect and install (recommended)
python install_ffmpeg.py

# Windows
winget install Gyan.FFmpeg       # built-in package manager
choco install ffmpeg             # Chocolatey
scoop install ffmpeg             # Scoop

# macOS
brew install ffmpeg

# Linux (Debian/Ubuntu)
sudo apt-get install -y ffmpeg

# Verify
ffmpeg -version
`

### Step 2 — Clone and Install Dependencies

`ash
git clone https://github.com/Duong-Phuoc-Hung/Flowkit-main.git
cd Flowkit-main
pip install -r requirements.txt

# Linux / macOS / WSL: one-command setup
./setup.sh
`

### Step 3 — Configure Environment

`ash
cp .env.example .env
# Edit .env with your API keys
`

| Variable | Default | Description |
|----------|---------|-------------|
| GEMINI_API_KEY | — | Google Gemini API key (script generation) |
| ANTHROPIC_API_KEY | — | Claude API key (optional) |
| API_PORT | 8100 | REST API port |
| API_COOLDOWN | 10 | Seconds between API calls |
| MAX_RETRIES | 5 | Max retries per failed request |

### Step 4 — Load Chrome Extension

1. Open chrome://extensions
2. Enable **Developer mode** (top-right toggle)
3. Click **Load unpacked** and select the extension/ folder
4. Open [labs.google/fx/tools/flow](https://labs.google/fx/tools/flow) and sign in

### Step 5 — Start the Agent

`ash
python -m agent.main
`

Verify the connection:

`ash
curl http://127.0.0.1:8100/health
# {"status": "ok", "extension_connected": true}
`

### Step 6 — Start Web Dashboard *(optional)*

`ash
cd flowkit-web
npm install
npm run dev
# Open http://localhost:3000
`

---

## Windows Quick Launch

Pre-built .bat launchers included:

| File | Action |
|------|--------|
| KHOI_DONG_APP.bat | Start agent + web dashboard |
| CHAY_TU_DONG.bat | Run full auto-factory pipeline |
| VONG_LAP_TIEN_HOA.bat | Continuous loop mode |
| KIEM_LOI_HE_THONG.bat | System diagnostics |
| TAO_ICON_RA_MAN_HINH.bat | Create desktop shortcut |

---

## Docker

`ash
docker-compose up -d
`

---

## AI Skills

35+ reusable workflow recipes in skills/ — compatible with Claude Code, Gemini CLI, and Codex CLI.

### Core Pipeline

| Skill | Description |
|-------|-------------|
| /fk:create-project | Interactive: create project, entities, video, scenes |
| /fk:gen-refs | Generate reference images for all entities |
| /fk:gen-images | Generate scene images (with reference inputs) |
| /fk:gen-videos | Render AI videos (8s each) |
| /fk:concat | Download, normalize, and concat all scene videos |
| /fk:status | Full project dashboard + next recommended action |
| /fk:pipeline | Smart full-pipeline orchestrator |

### Advanced Video

| Skill | Description |
|-------|-------------|
| /fk:gen-chain-videos | Start+end frame chaining for smooth transitions |
| /fk:insert-scene | Add multi-angle shots, cutaways, or close-ups |
| /fk:creative-mix | Analyze story + suggest optimal techniques |
| /fk:camera-guide | Cinematic camera, movement, and lighting guide |

### TTS and Narration

| Skill | Description |
|-------|-------------|
| /fk:gen-tts-template | Create voice anchor template |
| /fk:gen-narrator | Generate narrator text + TTS for all scenes |
| /fk:gen-text-overlays | Generate text overlays from narrator content |
| /fk:concat-fit-narrator | Trim videos to TTS duration, then concat |
| /fk:gen-music | Generate background music via Suno |

### YouTube Publishing

| Skill | Description |
|-------|-------------|
| /fk:youtube-seo | SEO-optimized title, description, and tags |
| /fk:brand-logo | Apply channel watermark and branding |
| /fk:thumbnail | Generate 4 YouTube-optimized thumbnail variants |
| /fk:youtube-upload | Upload with scheduling + rule validation |

### Utilities

| Skill | Description |
|-------|-------------|
| /fk:monitor | Full pipeline live monitor |
| /fk:doctor | Diagnose and fix errors across all layers |
| /fk:fix-uuids | Repair CAMS... media IDs to proper UUID format |
| /fk:refresh-urls | Refresh expired GCS signed URLs |
| /fk:research | Fact-check events before scripting |
| /fk:review-video | AI Vision quality review of generated videos |
| /fk:review-board | Visual scene review web app |
| /fk:switch-project | Switch active project context |

---

## Batch API

Submit multiple requests in one call. Server auto-throttles (max 5 concurrent, 10s cooldown):

`ash
curl -X POST http://127.0.0.1:8100/api/requests/batch \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {"type": "GENERATE_IMAGE", "scene_id": "<SID>", "project_id": "<PID>", "video_id": "<VID>", "orientation": "VERTICAL"},
      {"type": "GENERATE_IMAGE", "scene_id": "<SID>", "project_id": "<PID>", "video_id": "<VID>", "orientation": "VERTICAL"}
    ]
  }'
`

Poll aggregate status:

`ash
curl "http://127.0.0.1:8100/api/requests/batch-status?video_id=<VID>&type=GENERATE_IMAGE"
# {"total": 20, "pending": 5, "processing": 5, "completed": 10, "failed": 0, "done": false}
# When "done": true -> all requests finished (completed or failed)
`

---

## API Reference

### Resources

| Resource | Create | List | Get | Update | Delete |
|----------|--------|------|-----|--------|--------|
| Project | POST /api/projects | GET /api/projects | GET /api/projects/{id} | PATCH /api/projects/{id} | DELETE /api/projects/{id} |
| Character | POST /api/characters | GET /api/characters | GET /api/characters/{id} | PATCH /api/characters/{id} | DELETE /api/characters/{id} |
| Video | POST /api/videos | GET /api/videos?project_id= | GET /api/videos/{id} | PATCH /api/videos/{id} | DELETE /api/videos/{id} |
| Scene | POST /api/scenes | GET /api/scenes?video_id= | GET /api/scenes/{id} | PATCH /api/scenes/{id} | DELETE /api/scenes/{id} |

### Special Endpoints

| Endpoint | Description |
|----------|-------------|
| GET /health | Server health + extension connection status |
| GET /api/flow/credits | Remaining credits + account tier |
| GET /api/materials | Available image material/style options |
| POST /api/requests/batch | Submit multiple requests at once |
| GET /api/requests/batch-status | Poll batch completion status |

### Request Types

| Type | Description |
|------|-------------|
| GENERATE_IMAGE | Generate scene image (skips if already completed) |
| REGENERATE_IMAGE | Force-regenerate scene image |
| GENERATE_VIDEO | Render 8s AI video from scene image |
| GENERATE_VIDEO_REFS | Render video directly from reference images |
| UPSCALE_VIDEO | 4K upscale (TIER_TWO accounts only) |
| GENERATE_CHARACTER_IMAGE | Generate entity reference image |
| REGENERATE_CHARACTER_IMAGE | Force-regenerate entity reference image |

---

## Project Structure

`
flowkit-main/
|
+-- agent/                          # Python FastAPI backend
|   +-- main.py                     # FastAPI app + WebSocket server
|   +-- config.py                   # Configuration (loads models.json)
|   +-- models.json                 # Video & image model key mappings
|   +-- materials.py                # Image material/style system
|   +-- db/
|   |   +-- schema.py               # SQLite schema definitions
|   |   -- crud.py                 # Async CRUD operations
|   +-- models/                     # Pydantic request/response models
|   +-- api/                        # REST route handlers
|   |   +-- projects.py
|   |   +-- videos.py
|   |   +-- scenes.py
|   |   +-- characters.py
|   |   +-- requests.py
|   |   -- flow.py
|   +-- sdk/                        # Domain model SDK
|   |   +-- models/                 # Project, Video, Scene, Character
|   |   -- services/               # OperationService, result_handler
|   +-- services/
|   |   +-- flow_client.py          # WebSocket bridge to extension
|   |   +-- headers.py              # Randomized browser headers
|   |   -- post_process.py         # ffmpeg trim/merge/music
|   -- worker/
|       -- processor.py            # Async queue processor
|
+-- factory/                        # Auto-production pipeline
|   +-- stage_1_script.py           # AI script generation (Gemini)
|   +-- stage_2_images.py           # Reference + scene image generation
|   +-- stage_3_videos.py           # AI video rendering
|   +-- stage_4_concat.py           # ffmpeg concat + BGM mixing
|   -- stage_5_upload.py           # YouTube upload automation
|
+-- flowkit-web/                    # Next.js 15 web dashboard
|   -- src/app/                    # Stations 1-5, AI analysis, config
|
+-- extension/                      # Chrome MV3 extension
|   +-- manifest.json
|   +-- background.js               # WebSocket bridge + token capture
|   +-- content.js                  # reCAPTCHA auto-solver
|   -- popup.html / popup.js       # Live dashboard UI
|
+-- skills/                         # 35+ AI agent workflow recipes
+-- scripts/                        # Helper scripts
+-- tools/                          # Utility tools
+-- tests/                          # E2E test suite
|
+-- auto_factory.py                 # Main factory orchestrator
+-- install_ffmpeg.py               # Cross-platform ffmpeg installer
+-- setup.py                        # Project setup script
+-- setup.sh                        # Unix one-command setup
+-- requirements.txt
+-- docker-compose.yml
+-- Dockerfile
+-- .env.example
|
+-- KHOI_DONG_APP.bat               # [Windows] Launch app
+-- CHAY_TU_DONG.bat                # [Windows] Run auto pipeline
+-- VONG_LAP_TIEN_HOA.bat           # [Windows] Continuous loop
-- KIEM_LOI_HE_THONG.bat           # [Windows] System diagnostics
`

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| API_HOST | 127.0.0.1 | REST API bind address |
| API_PORT | 8100 | REST API port |
| WS_PORT | 9222 | WebSocket server port |
| POLL_INTERVAL | 5 | Worker poll cycle in seconds |
| MAX_RETRIES | 5 | Maximum retries per request |
| VIDEO_POLL_TIMEOUT | 420 | Video generation timeout (seconds) |
| API_COOLDOWN | 10 | Cooldown between API calls (seconds) |

---

## Troubleshooting

| Symptom | Solution |
|---------|----------|
| Extension shows "Agent disconnected" | Run python -m agent.main |
| Extension shows "No token" | Open labs.google/fx/tools/flow and sign in |
| CAPTCHA_FAILED: NO_FLOW_TAB | Open a Google Flow tab |
| HTTP 403 MODEL_ACCESS_DENIED | Downgrade model in models.json |
| media_id starts with CAMS... | Run /fk:fix-uuids |
| Scene images visually inconsistent | Ensure all entity refs have UUID media_id |
| Upscale returns "permission denied" | Requires PAYGATE_TIER_TWO account |
| YouTube upload invalidTags | Tags exceed 500-char limit, reduce count |
| fmpeg: command not found | Run python install_ffmpeg.py |
| Request stuck in PROCESSING | Restart Chrome extension WebSocket |

---

## License

[MIT](LICENSE)

---

## Community

<div align="center">

[![Join on Facebook](https://img.shields.io/badge/Community-FlowKit_%26_Flowboard_on_Facebook-1877F2?style=for-the-badge&logo=facebook&logoColor=white)](https://www.facebook.com/groups/flowkit.flowboard.community)

**[facebook.com/groups/flowkit.flowboard.community](https://www.facebook.com/groups/flowkit.flowboard.community)**

Share generated videos · Ask for help · Request features · Report bugs

</div>
