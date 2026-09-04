# FlowKit

<div align="center">

**End-to-End AI Video Production — From Story Idea to YouTube, Fully Automated**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![Next.js 15](https://img.shields.io/badge/Next.js-15-black?logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Chrome MV3](https://img.shields.io/badge/Chrome-MV3-4285F4?logo=googlechrome&logoColor=white)](extension/)
[![ffmpeg](https://img.shields.io/badge/ffmpeg-required-007808)](https://ffmpeg.org)

[Getting Started](#getting-started) &nbsp;·&nbsp;
[Architecture](#architecture) &nbsp;·&nbsp;
[AI Skills](#ai-skills) &nbsp;·&nbsp;
[API Reference](#api-reference) &nbsp;·&nbsp;
[Community](#community)

</div>

---

## What is FlowKit?

FlowKit is an **automated AI video production system** that connects Google Flow's image/video generation API to a local orchestration engine. It handles the entire pipeline — script writing, image generation, video rendering, post-processing, and YouTube upload — with minimal manual intervention.

**Core flow:**
```
Idea  →  AI Script  →  Reference Images  →  Scene Images
     →  AI Videos (8 s/clip)  →  Concat + BGM  →  YouTube
```

**Tech stack:**
- **Backend:** Python 3.10, FastAPI, SQLite (aiosqlite)
- **Browser Bridge:** Chrome Extension (Manifest V3)
- **Frontend:** Next.js 15 (App Router)
- **Post-processing:** ffmpeg, OmniVoice TTS, Suno music
- **AI:** Google Flow API, Gemini, Claude Vision

---

## Architecture

```
┌─────────────────────────┐   WebSocket :9222   ┌──────────────────────────┐
│      Python Agent       │ ◄─────────────────► │    Chrome Extension      │
│   FastAPI  ·  SQLite    │                     │    Manifest V3           │
│                         │                     │                          │
│  REST API      :8100    │  ──── commands ────► │  · Capture token ya29.*  │
│  Queue Worker (5 conc.) │  ◄─── responses ─── │  · Solve reCAPTCHA v2    │
│  SQLite DB              │                     │  · Proxy Flow API calls  │
│  Post-process (ffmpeg)  │                     │  · Live dashboard UI     │
│  TTS · Music · Review   │                     │                          │
└────────────┬────────────┘                     └──────────────────────────┘
             │
             │ HTTP :3000
             ▼
┌─────────────────────────┐                     ┌──────────────────────────┐
│   Auto Factory          │                     │   Web Dashboard          │
│   5-stage pipeline      │ ◄─────────────────► │   Next.js 15             │
│                         │                     │                          │
│  1. Script   (Gemini)   │                     │  / ·····  Submit idea    │
│  2. Images              │                     │  /tram-2  Review script  │
│  3. Videos              │                     │  /tram-3  Render monitor │
│  4. Concat + BGM        │                     │  /tram-4  Final output   │
│  5. YouTube Upload      │                     │  /tram-5  Publish        │
└─────────────────────────┘                     └──────────────────────────┘
```

---

## Components

### Python Agent (`agent/`)

The backend that owns the database, job queue, and all orchestration logic.

| Module | Role |
|--------|------|
| `api/projects.py` | CRUD for projects |
| `api/videos.py` | CRUD for videos |
| `api/scenes.py` | CRUD for scenes |
| `api/characters.py` | CRUD for characters / entities |
| `api/requests.py` | Job queue: submit & poll generation requests |
| `api/flow.py` | Credits, materials, model info |
| `api/reviews.py` | AI Vision video review (Claude) |
| `api/tts.py` | OmniVoice TTS narration |
| `api/music.py` | Suno background music |
| `api/models.py` | Model key management |
| `sdk/` | Domain layer: `Project`, `Video`, `Scene`, `Character` |
| `worker/processor.py` | Async queue (max 5 concurrent, 10 s cooldown) |
| `services/flow_client.py` | WebSocket bridge to Chrome extension |
| `services/post_process.py` | ffmpeg trim, merge, audio mixing |

### Chrome Extension (`extension/`)

A Manifest V3 Service Worker that bridges the agent to Google Flow.

| File | Role |
|------|------|
| `background.js` | WebSocket server · token capture · API proxy |
| `content.js` | reCAPTCHA v2 auto-solver |
| `popup.html/js` | Live dashboard: progress, logs, connection status |

### Auto Factory (`factory/`)

Sequential 5-stage pipeline driven by `auto_factory.py`.

| Stage | File | Output |
|-------|------|--------|
| 1 | `stage_1_script.py` | Full scene script (Gemini) |
| 2 | `stage_2_images.py` | Reference images + scene frames |
| 3 | `stage_3_videos.py` | 8-second AI video per scene |
| 4 | `stage_4_concat.py` | Merged video + BGM (ffmpeg) |
| 5 | `stage_5_upload.py` | Published YouTube video |

### Web Dashboard (`flowkit-web/`)

Next.js 15 pipeline control panel.

| Route | Purpose |
|-------|---------|
| `/` | Submit story idea — Station 1 |
| `/tram-2` | Review & edit AI script — Station 2 |
| `/tram-2-5` | Approve reference images — Station 2.5 |
| `/tram-3` | Monitor scene rendering — Station 3 |
| `/diep-vien` | Manage characters / entities |
| `/tram-4` | Preview final video — Station 4 |
| `/tram-5` | YouTube upload & publish — Station 5 |
| `/ai-phan-tich` | AI quality analysis |
| `/cau-hinh` | System configuration |

---

## Getting Started

### Requirements

| Tool | Version | Required |
|------|---------|----------|
| Python | 3.10+ | ✅ |
| pip | latest | ✅ |
| Google Chrome | latest | ✅ |
| ffmpeg | any | ✅ |
| Node.js | 18+ | Web dashboard only |

---

### 1 · Install ffmpeg

```bash
# Recommended — auto-detects OS and installs
python install_ffmpeg.py

# Windows (pick one)
winget install Gyan.FFmpeg
choco install ffmpeg
scoop install ffmpeg

# macOS
brew install ffmpeg

# Linux (Debian / Ubuntu)
sudo apt-get install -y ffmpeg

# Verify
ffmpeg -version
```

---

### 2 · Install Python dependencies

```bash
git clone https://github.com/Duong-Phuoc-Hung/Flowkit-main.git
cd Flowkit-main

pip install -r requirements.txt

# Linux / macOS / WSL: automated setup
./setup.sh
```

---

### 3 · Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your keys:

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_API_KEY` | — | Google Flow API key *(required)* |
| `ANTHROPIC_API_KEY` | — | Claude key for AI video review |
| `SUNO_API_KEY` | — | Suno key for background music |
| `API_HOST` | `127.0.0.1` | Agent REST bind address |
| `API_PORT` | `8100` | Agent REST port |
| `WS_HOST` | `127.0.0.1` | WebSocket bind address |
| `WS_PORT` | `9222` | WebSocket port (extension connects here) |
| `MAX_CONCURRENT_REQUESTS` | `5` | Parallel generation slots |
| `API_COOLDOWN` | `10` | Seconds between API calls |
| `VIDEO_POLL_TIMEOUT` | `420` | Max wait for one video (seconds) |

---

### 4 · Load Chrome Extension

1. Open `chrome://extensions`
2. Enable **Developer mode** (top-right toggle)
3. Click **Load unpacked** → select the `extension/` folder
4. Open **[labs.google/fx/tools/flow](https://labs.google/fx/tools/flow)** and sign in

The extension status dot turns **green** when connected to the agent.

---

### 5 · Start the agent

```bash
python -m agent.main
```

Check the connection:

```bash
curl http://127.0.0.1:8100/health
# {"status": "ok", "extension_connected": true}
```

---

### 6 · Start the web dashboard *(optional)*

```bash
cd flowkit-web
npm install
npm run dev
# Open http://localhost:3000
```

---

## Windows Quick Launch

| File | What it does |
|------|-------------|
| `KHOI_DONG_APP.bat` | Start agent + web dashboard |
| `CHAY_TU_DONG.bat` | Run the full auto-factory pipeline |
| `VONG_LAP_TIEN_HOA.bat` | Continuous production loop |
| `KIEM_LOI_HE_THONG.bat` | Run system diagnostics |
| `TAO_ICON_RA_MAN_HINH.bat` | Create a desktop shortcut |

---

## Docker

```bash
# Start both backend (:8100) and frontend (:3000)
docker-compose up -d

# Backend only
docker build -t flowkit .
docker run -p 8100:8100 -p 9222:9222 flowkit
```

---

## AI Skills

35+ workflow recipes in `skills/` — works with Claude Code, Gemini CLI, and Codex CLI.
Invoke any skill by typing its name in the agent chat.

### Core Pipeline

| Skill | What it does |
|-------|-------------|
| `/fk:create-project` | Guided setup: project → entities → video → scenes |
| `/fk:gen-refs` | Generate reference images for all entities |
| `/fk:gen-images` | Generate scene images (uses reference inputs) |
| `/fk:gen-videos` | Render 8-second AI video per scene |
| `/fk:concat` | Download, normalize, and merge all scene clips |
| `/fk:pipeline` | Smart full-pipeline orchestrator |
| `/fk:status` | Live project dashboard + next recommended action |

### Video Techniques

| Skill | What it does |
|-------|-------------|
| `/fk:gen-chain-videos` | Start-to-end frame chaining for smooth transitions |
| `/fk:insert-scene` | Add cutaways, close-ups, or multi-angle shots |
| `/fk:creative-mix` | Analyze story + recommend optimal techniques |
| `/fk:camera-guide` | Cinematic camera, motion, and lighting reference |

### TTS & Narration

| Skill | What it does |
|-------|-------------|
| `/fk:gen-tts-template` | Create a voice anchor template |
| `/fk:gen-narrator` | Write narrator text + generate TTS for all scenes |
| `/fk:gen-text-overlays` | Build text overlays from narrator content |
| `/fk:concat-fit-narrator` | Trim clips to TTS duration, then merge |
| `/fk:gen-music` | Generate background music via Suno |

### YouTube Publishing

| Skill | What it does |
|-------|-------------|
| `/fk:youtube-seo` | SEO title, description, tags, chapters |
| `/fk:brand-logo` | Watermark + channel branding |
| `/fk:thumbnail` | Generate 4 YouTube-optimised thumbnail variants |
| `/fk:youtube-upload` | Upload + schedule with rule validation |

### Utilities

| Skill | What it does |
|-------|-------------|
| `/fk:monitor` | Live pipeline progress monitor |
| `/fk:doctor` | Diagnose errors across all layers |
| `/fk:fix-uuids` | Repair `CAMS...` media IDs → proper UUID |
| `/fk:refresh-urls` | Refresh expired GCS signed URLs |
| `/fk:research` | Fact-check before writing script |
| `/fk:review-video` | AI Vision quality review of generated clips |
| `/fk:review-board` | Visual scene board web app |

---

## Batch API

Submit all requests at once — the server throttles automatically.

```bash
# Submit a batch
curl -X POST http://127.0.0.1:8100/api/requests/batch \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "type": "GENERATE_IMAGE",
        "scene_id": "<scene-uuid>",
        "project_id": "<project-uuid>",
        "video_id": "<video-uuid>",
        "orientation": "VERTICAL"
      }
    ]
  }'

# Poll until done
curl "http://127.0.0.1:8100/api/requests/batch-status?video_id=<VID>&type=GENERATE_IMAGE"
# {
#   "total": 20, "pending": 0, "processing": 0,
#   "completed": 18, "failed": 2,
#   "done": true, "all_succeeded": false
# }
```

**Rules:**
- `GENERATE_*` — skips requests that are already `COMPLETED`
- `REGENERATE_*` — always re-runs (clears downstream results first)
- Max 5 concurrent · 10 s cooldown enforced by the worker

---

## API Reference

### CRUD endpoints

| Resource | Create | List | Get | Update | Delete |
|----------|--------|------|-----|--------|--------|
| Project | `POST /api/projects` | `GET /api/projects` | `GET /api/projects/{id}` | `PATCH /api/projects/{id}` | `DELETE /api/projects/{id}` |
| Character | `POST /api/characters` | `GET /api/characters` | `GET /api/characters/{id}` | `PATCH /api/characters/{id}` | `DELETE /api/characters/{id}` |
| Video | `POST /api/videos` | `GET /api/videos?project_id=` | `GET /api/videos/{id}` | `PATCH /api/videos/{id}` | `DELETE /api/videos/{id}` |
| Scene | `POST /api/scenes` | `GET /api/scenes?video_id=` | `GET /api/scenes/{id}` | `PATCH /api/scenes/{id}` | `DELETE /api/scenes/{id}` |

### Utility endpoints

| Endpoint | Description |
|----------|-------------|
| `GET  /health` | Server health + extension connection |
| `GET  /api/flow/credits` | Remaining credits + account tier |
| `GET  /api/materials` | Available image style options |
| `GET  /api/models` | Active video / image model keys |
| `POST /api/requests/batch` | Submit multiple generation jobs |
| `GET  /api/requests/batch-status` | Poll batch completion |
| `POST /api/videos/{id}/narrate` | Trigger TTS narration for a video |

### Request types

| Type | Behaviour |
|------|-----------|
| `GENERATE_IMAGE` | Generate scene image — skip if already done |
| `REGENERATE_IMAGE` | Force regenerate scene image |
| `GENERATE_VIDEO` | Render 8 s video from scene image |
| `GENERATE_VIDEO_REFS` | Render video directly from reference images |
| `UPSCALE_VIDEO` | 4 K upscale (TIER_TWO accounts only) |
| `GENERATE_CHARACTER_IMAGE` | Generate entity reference image |
| `REGENERATE_CHARACTER_IMAGE` | Force regenerate entity reference |

---

## Project Structure

```
flowkit-main/
├── agent/                       # Python FastAPI backend
│   ├── main.py                  # App entry point + WebSocket server
│   ├── config.py                # Settings (reads .env + models.json)
│   ├── models.json              # Video & image model key mappings
│   ├── materials.py             # Image style / material system
│   ├── db/
│   │   ├── schema.py            # SQLite table definitions
│   │   └── crud.py              # Async CRUD helpers
│   ├── models/                  # Pydantic request/response schemas
│   ├── api/                     # FastAPI route modules
│   │   ├── projects.py
│   │   ├── videos.py
│   │   ├── scenes.py
│   │   ├── characters.py
│   │   ├── requests.py
│   │   ├── flow.py
│   │   ├── reviews.py           # Claude Vision review
│   │   ├── tts.py               # OmniVoice TTS
│   │   ├── music.py             # Suno music
│   │   ├── models.py            # Model key management
│   │   └── active_project.py
│   ├── sdk/                     # Domain model SDK
│   │   ├── models/              # Project · Video · Scene · Character
│   │   └── services/            # OperationService · result_handler
│   ├── services/
│   │   ├── flow_client.py       # WebSocket bridge to extension
│   │   ├── event_bus.py         # Internal pub/sub
│   │   └── post_process.py      # ffmpeg trim · merge · music
│   └── worker/
│       └── processor.py         # Async job queue (5 concurrent)
│
├── factory/                     # 5-stage auto-production pipeline
│   ├── stage_1_script.py        # Script generation (Gemini)
│   ├── stage_2_images.py        # Reference + scene images
│   ├── stage_3_videos.py        # AI video rendering
│   ├── stage_4_concat.py        # ffmpeg concat + BGM
│   └── stage_5_upload.py        # YouTube upload
│
├── flowkit-web/                 # Next.js 15 web dashboard
│   └── src/app/
│       ├── page.tsx             # Station 1 — submit idea
│       ├── tram-2/              # Station 2 — review script
│       ├── tram-2-5/            # Station 2.5 — approve refs
│       ├── tram-3/              # Station 3 — render monitor
│       ├── tram-4/              # Station 4 — final output
│       ├── tram-5/              # Station 5 — YouTube publish
│       ├── diep-vien/           # Character / entity manager
│       ├── ai-phan-tich/        # AI video analysis
│       └── cau-hinh/            # System config
│
├── extension/                   # Chrome MV3 extension
│   ├── manifest.json
│   ├── background.js            # WS bridge + token capture
│   ├── content.js               # reCAPTCHA auto-solver
│   └── popup.html / popup.js    # Live dashboard UI
│
├── skills/                      # 35+ AI agent skill files
├── scripts/                     # Utility scripts
├── tools/                       # CLI tools
├── tests/                       # Test suite (pytest)
│
├── auto_factory.py              # Factory pipeline entry point
├── install_ffmpeg.py            # Cross-platform ffmpeg installer
├── setup.py                     # Project setup automation
├── setup.sh                     # Unix one-command setup
├── requirements.txt             # Python dependencies
├── docker-compose.yml           # Backend + frontend services
├── Dockerfile                   # Backend image
├── .env.example                 # Environment template
│
├── KHOI_DONG_APP.bat            # [Win] Launch app
├── CHAY_TU_DONG.bat             # [Win] Run auto pipeline
├── VONG_LAP_TIEN_HOA.bat        # [Win] Continuous loop
└── KIEM_LOI_HE_THONG.bat        # [Win] System diagnostics
```

---

## Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `API_HOST` | `127.0.0.1` | REST API bind address |
| `API_PORT` | `8100` | REST API port |
| `WS_HOST` | `127.0.0.1` | WebSocket bind address |
| `WS_PORT` | `9222` | WebSocket port |
| `POLL_INTERVAL` | `5` | Worker poll cycle (seconds) |
| `MAX_RETRIES` | `5` | Retries before marking a job failed |
| `MAX_CONCURRENT_REQUESTS` | `5` | Parallel generation slots |
| `API_COOLDOWN` | `10` | Seconds between API calls |
| `VIDEO_POLL_TIMEOUT` | `420` | Max wait for video generation (seconds) |
| `STALE_PROCESSING_TIMEOUT` | `600` | Timeout for stuck jobs (seconds) |
| `TTS_MODEL` | `k2-fsa/OmniVoice` | TTS model |
| `REVIEW_MODEL` | `claude-haiku-4-5` | Claude model for video review |
| `SUNO_MODEL` | `V4` | Suno music generation model |

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Extension shows **"Agent disconnected"** | Run `python -m agent.main` |
| Extension shows **"No token"** | Open `labs.google/fx/tools/flow` and sign in |
| `CAPTCHA_FAILED: NO_FLOW_TAB` | Keep a Google Flow tab open in Chrome |
| HTTP 403 `MODEL_ACCESS_DENIED` | Downgrade model in `models.json`; check `/api/flow/credits` |
| `media_id` starts with `CAMS...` | Run `/fk:fix-uuids` |
| Scene images look inconsistent | All entity reference images must have a UUID `media_id` |
| Upscale returns **"permission denied"** | Requires a `PAYGATE_TIER_TWO` account |
| YouTube `invalidTags` error | Tag string exceeds 500 characters — remove some tags |
| `ffmpeg: command not found` | Run `python install_ffmpeg.py` |
| Request stuck in `PROCESSING` | Restart the Chrome extension or reload the agent |

---

## License

[MIT](LICENSE) — free to use, modify, and distribute.

---

## Community

<div align="center">

<br/>

[![Join FlowKit & Flowboard on Facebook](https://img.shields.io/static/v1?label=Facebook+Group&message=FlowKit+%26+Flowboard&color=1877F2&style=for-the-badge&logo=facebook&logoColor=white)](https://www.facebook.com/groups/flowkit.flowboard.community)

<br/><br/>

**[facebook.com/groups/flowkit.flowboard.community](https://www.facebook.com/groups/flowkit.flowboard.community)**

Share generated videos · Ask for help · Request features · Report bugs

</div>
