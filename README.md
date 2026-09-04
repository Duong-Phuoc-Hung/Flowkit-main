<p align="center">
  <img src="docs/images/flowkit_banner.svg" width="720" alt="FLOW KIT" />
</p>

<p align="center">
  <a href="#license"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"/></a>
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="Python 3.10+"/>
  <img src="https://img.shields.io/badge/Next.js-15-black?logo=nextdotjs&logoColor=white" alt="Next.js 15"/>
  <img src="https://img.shields.io/badge/Chrome-MV3-4285F4?logo=googlechrome&logoColor=white" alt="Chrome MV3"/>
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/ffmpeg-required-007808?logo=ffmpeg&logoColor=white" alt="ffmpeg"/>
  <a href="CLAUDE.md"><img src="https://img.shields.io/badge/Docs-CLAUDE.md-8A2BE2" alt="Documentation"/></a>
</p>

# FLOW KIT

H? th?ng s?n xu?t video AI t? d?ng hoàn ch?nh, t? ý tu?ng d?n video YouTube — s? d?ng **Google Flow API** thông qua Chrome extension làm c?u n?i xác th?c.

---

## T?ng quan ki?n trúc

```
+---------------------+      WebSocket       +--------------------------+
¦   Python Agent      ¦?--------------------?¦   Chrome Extension        ¦
¦   (FastAPI+SQLite)  ¦     localhost:9222    ¦   (MV3 Service Worker)    ¦
¦                     ¦                      ¦                           ¦
¦  REST API :8100     ¦  -- commands --?      ¦  - Token capture          ¦
¦  Queue worker       ¦  ?-- results --       ¦  - reCAPTCHA solve        ¦
¦  SQLite DB          ¦                      ¦  - API proxy              ¦
¦  Post-process       ¦                      ¦  (on labs.google)         ¦
+---------------------+                      +--------------------------+
          ¦
          ?
+---------------------+      HTTP :3000      +--------------------------+
¦   factory/          ¦?--------------------?¦   flowkit-web             ¦
¦   (Auto Pipeline)   ¦                      ¦   (Next.js Dashboard)     ¦
¦                     ¦                      ¦                           ¦
¦  stage_1_script.py  ¦                      ¦  Tr?m 1: Nh?p ý tu?ng    ¦
¦  stage_2_images.py  ¦                      ¦  Tr?m 2: Duy?t k?ch b?n  ¦
¦  stage_3_videos.py  ¦                      ¦  Tr?m 3: Render ?nh/video ¦
¦  stage_4_concat.py  ¦                      ¦  Tr?m 4: Hoàn thành       ¦
¦  stage_5_upload.py  ¦                      ¦  Tr?m 5: YouTube upload   ¦
+---------------------+                      +--------------------------+
```

---

## Thành ph?n d? án

### 1. Chrome Extension (`extension/`)
- B?t token Google Flow (`ya29.*`) t? `aisandbox-pa.googleapis.com`
- T? d?ng gi?i reCAPTCHA v2
- Proxy toàn b? Google Flow API v? local agent qua WebSocket
- Hi?n th? Live Dashboard: request log, progress, tr?ng thái k?t n?i

### 2. Python Agent (`agent/`)
- **FastAPI** REST API trên c?ng `8100`
- **SQLite** (aiosqlite) luu projects, videos, scenes, characters, requests
- **Queue worker**: x? lý t?i da 5 requests d?ng th?i, cooldown 10s
- **SDK domain model**: `Project`, `Video`, `Scene`, `Character` v?i 2 ch? d? th?c thi (queue & direct)
- **Post-processing**: ffmpeg trim/merge, mix nh?c n?n

### 3. Auto Factory (`factory/`, `auto_factory.py`)
Pipeline t? d?ng 5 giai do?n:

| Stage | File | Mô t? |
|-------|------|--------|
| 1 | `stage_1_script.py` | AI sinh k?ch b?n t? ý tu?ng (Gemini) |
| 2 | `stage_2_images.py` | Sinh reference images + scene images |
| 3 | `stage_3_videos.py` | Render video AI (8s/scene) |
| 4 | `stage_4_concat.py` | ffmpeg concat + mix BGM |
| 5 | `stage_5_upload.py` | Upload YouTube t? d?ng |

### 4. Web Dashboard (`flowkit-web/`)
Next.js 15 app — giao di?n di?u khi?n pipeline theo "tr?m":

| Trang | Route | Ch?c nang |
|-------|-------|-----------|
| Tr?m 1 | `/` | Nh?p ý tu?ng, d?t tên d? án, g?i k?ch b?n |
| Tr?m 2 | `/tram-2` | Duy?t & ch?nh s?a k?ch b?n AI sinh ra |
| Tr?m 2.5 | `/tram-2-5` | Duy?t ?nh reference tru?c khi render |
| Tr?m 3 | `/tram-3` | Theo dõi render ?nh scene |
| Tr?m 3.8 | `/diep-vien` | Qu?n lý nhân v?t/di?p viên |
| Tr?m 4 | `/tram-4` | Xem k?t qu? video hoàn ch?nh |
| Tr?m 5 | `/tram-5` | Upload YouTube |
| AI Phân Tích | `/ai-phan-tich` | Phân tích ch?t lu?ng video b?ng AI |
| C?u Hình | `/cau-hinh` | Cài d?t h? th?ng |

---

## Cài d?t

### Yêu c?u
- Python 3.10+
- Node.js 18+ (cho web dashboard)
- Google Chrome
- ffmpeg

### Bu?c 1: Cài ffmpeg

```bash
# Auto-install (recommended)
python install_ffmpeg.py

# Ho?c th? công trên Windows
winget install Gyan.FFmpeg

# macOS
brew install ffmpeg

# Linux
sudo apt-get install -y ffmpeg
```

### Bu?c 2: Cài Python dependencies

```bash
pip install -r requirements.txt
```

Ho?c dùng script setup t? d?ng:

```bash
# Linux/macOS/WSL
./setup.sh
```

### Bu?c 3: C?u hình môi tru?ng

```bash
cp .env.example .env
# Ch?nh s?a .env v?i các API key c?n thi?t
```

Các bi?n quan tr?ng trong `.env`:

| Bi?n | Mô t? |
|------|-------|
| `GEMINI_API_KEY` | Google Gemini API key (cho sinh k?ch b?n) |
| `ANTHROPIC_API_KEY` | Claude API key (tu? ch?n) |
| `API_HOST` | Ð?a ch? bind REST API (m?c d?nh: `127.0.0.1`) |
| `API_PORT` | C?ng REST API (m?c d?nh: `8100`) |
| `API_COOLDOWN` | Giây ngh? gi?a các API call (m?c d?nh: `10`) |

### Bu?c 4: Cài Chrome Extension

1. M? `chrome://extensions`
2. B?t **Developer mode**
3. Ch?n **Load unpacked** ? ch?n thu m?c `extension/`
4. M? [labs.google/fx/tools/flow](https://labs.google/fx/tools/flow) và dang nh?p

### Bu?c 5: Ch?y Agent

```bash
python -m agent.main
```

Ki?m tra k?t n?i:
```bash
curl http://127.0.0.1:8100/health
# {"status": "ok", "extension_connected": true}
```

### Bu?c 6: Ch?y Web Dashboard (tu? ch?n)

```bash
cd flowkit-web
npm install
npm run dev
# M? http://localhost:3000
```

---

## Ch?y nhanh trên Windows

D? án có s?n các file `.bat` d? ch?y nhanh:

| File | Ch?c nang |
|------|-----------|
| `KHOI_DONG_APP.bat` | Kh?i d?ng agent + web dashboard |
| `CHAY_TU_DONG.bat` | Ch?y auto factory pipeline |
| `VONG_LAP_TIEN_HOA.bat` | Vòng l?p t? d?ng liên t?c |
| `KIEM_LOI_HE_THONG.bat` | Ki?m tra l?i h? th?ng |
| `TAO_ICON_RA_MAN_HINH.bat` | T?o shortcut desktop |

---

## Docker

```bash
docker-compose up -d
```

Ho?c build th? công:
```bash
docker build -t flowkit .
docker run -p 8100:8100 flowkit
```

---

## Pipeline AI Skills

Các workflow t? d?ng cho AI agent (Claude Code, Gemini CLI, Codex CLI) trong thu m?c `skills/`:

### Pipeline co b?n
| Skill | Mô t? |
|-------|-------|
| `/fk:create-project` | T?o project + entities + video + scenes |
| `/fk:gen-refs` | Sinh reference images cho t?t c? entities |
| `/fk:gen-images` | Sinh scene images |
| `/fk:gen-videos` | Render video AI |
| `/fk:concat` | Ghép video + mix nh?c |
| `/fk:status` | Dashboard tr?ng thái project |

### Video nâng cao
| Skill | Mô t? |
|-------|-------|
| `/fk:gen-chain-videos` | Video chaining (start+end frame transitions) |
| `/fk:insert-scene` | Chèn scene m?i (multi-angle, cutaway) |
| `/fk:creative-mix` | Phân tích + d? xu?t k? thu?t t?i uu |
| `/fk:camera-guide` | Hu?ng d?n góc máy, chuy?n d?ng, ánh sáng |

### TTS & Thuy?t minh
| Skill | Mô t? |
|-------|-------|
| `/fk:gen-tts-template` | T?o voice template |
| `/fk:gen-narrator` | Sinh text thuy?t minh + TTS |
| `/fk:gen-text-overlays` | T?o text overlay t? narrator |
| `/fk:concat-fit-narrator` | C?t video fit theo TTS r?i ghép |

### YouTube
| Skill | Mô t? |
|-------|-------|
| `/fk:youtube-seo` | Sinh metadata SEO (title, description, tags) |
| `/fk:brand-logo` | Thêm logo/watermark kênh |
| `/fk:thumbnail` | T?o 4 thumbnail variants |
| `/fk:youtube-upload` | Upload t? d?ng v?i l?ch dang |

### Ti?n ích
| Skill | Mô t? |
|-------|-------|
| `/fk:pipeline` | Orchestrator toàn pipeline thông minh |
| `/fk:monitor` | Theo dõi toàn b? pipeline |
| `/fk:doctor` | Ch?n doán và s?a l?i |
| `/fk:fix-uuids` | S?a media_id format sai (CAMS... ? UUID) |
| `/fk:refresh-urls` | Làm m?i signed URLs h?t h?n |
| `/fk:research` | Ki?m ch?ng s? ki?n tru?c khi vi?t k?ch b?n |

---

## Batch API

G?i nhi?u requests cùng lúc (server t? throttle — max 5 d?ng th?i, cooldown 10s):

```bash
curl -X POST http://127.0.0.1:8100/api/requests/batch \
  -H "Content-Type: application/json" \
  -d '{"requests": [
    {"type": "GENERATE_IMAGE", "scene_id": "...", "project_id": "...", "video_id": "...", "orientation": "VERTICAL"},
    {"type": "GENERATE_IMAGE", "scene_id": "...", "project_id": "...", "video_id": "...", "orientation": "VERTICAL"}
  ]}'
```

Poll tr?ng thái:
```bash
curl "http://127.0.0.1:8100/api/requests/batch-status?video_id=<VID>&type=GENERATE_IMAGE"
# {"total": 20, "pending": 10, "processing": 5, "completed": 5, "failed": 0, "done": false}
```

---

## API Reference

### Endpoints chính

| Resource | Create | List | Get | Update | Delete |
|----------|--------|------|-----|--------|--------|
| Project | `POST /api/projects` | `GET /api/projects` | `GET /api/projects/{id}` | `PATCH /api/projects/{id}` | `DELETE /api/projects/{id}` |
| Character | `POST /api/characters` | `GET /api/characters` | `GET /api/characters/{id}` | `PATCH /api/characters/{id}` | `DELETE /api/characters/{id}` |
| Video | `POST /api/videos` | `GET /api/videos?project_id=` | `GET /api/videos/{id}` | `PATCH /api/videos/{id}` | `DELETE /api/videos/{id}` |
| Scene | `POST /api/scenes` | `GET /api/scenes?video_id=` | `GET /api/scenes/{id}` | `PATCH /api/scenes/{id}` | `DELETE /api/scenes/{id}` |
| Request | `POST /api/requests` | `GET /api/requests` | `GET /api/requests/{id}` | — | — |

### Endpoints d?c bi?t

| Endpoint | Mô t? |
|----------|-------|
| `GET /health` | Tr?ng thái server + extension |
| `GET /api/flow/credits` | Credits + tier ngu?i dùng |
| `GET /api/materials` | Danh sách materials (style) |
| `POST /api/requests/batch` | G?i nhi?u requests cùng lúc |
| `GET /api/requests/batch-status` | Poll tr?ng thái batch |

### Lo?i Request

| Type | Mô t? |
|------|-------|
| `GENERATE_IMAGE` | Sinh ?nh scene (b? qua n?u dã xong) |
| `REGENERATE_IMAGE` | Sinh l?i ?nh scene (xóa + làm m?i) |
| `GENERATE_VIDEO` | Render video t? ?nh |
| `GENERATE_VIDEO_REFS` | Render video t? reference images |
| `UPSCALE_VIDEO` | Upscale 4K (TIER_TWO) |
| `GENERATE_CHARACTER_IMAGE` | Sinh reference image entity |
| `REGENERATE_CHARACTER_IMAGE` | Sinh l?i reference image |

---

## C?u trúc thu m?c

```
flowkit-main/
+-- agent/                    # Python FastAPI backend
¦   +-- main.py               # FastAPI app + WebSocket server
¦   +-- config.py             # C?u hình (loads models.json)
¦   +-- models.json           # Video/image model mappings
¦   +-- materials.py          # Material system
¦   +-- db/                   # SQLite schema + CRUD
¦   +-- models/               # Pydantic models (API layer)
¦   +-- api/                  # REST routes
¦   +-- sdk/                  # Domain model SDK
¦   ¦   +-- models/           # Project, Video, Scene, Character
¦   ¦   +-- services/         # OperationService, result_handler
¦   +-- services/             # flow_client, headers, post_process
¦   +-- worker/               # Queue processor
¦
+-- factory/                  # Auto pipeline (5 stages)
¦   +-- stage_1_script.py     # AI script generation
¦   +-- stage_2_images.py     # Image generation
¦   +-- stage_3_videos.py     # Video rendering
¦   +-- stage_4_concat.py     # ffmpeg concat + BGM
¦   +-- stage_5_upload.py     # YouTube upload
¦
+-- flowkit-web/              # Next.js 15 web dashboard
¦   +-- src/app/              # Pages: tram-1 ? tram-5, ai-phan-tich, cau-hinh
¦
+-- extension/                # Chrome MV3 extension
¦   +-- manifest.json
¦   +-- background.js         # WebSocket bridge + token capture
¦   +-- content.js            # reCAPTCHA solver
¦   +-- popup.html/js         # Live dashboard UI
¦
+-- skills/                   # AI agent workflow recipes (35+ skills)
+-- scripts/                  # Helper scripts
+-- tools/                    # Utility tools
+-- tests/                    # E2E tests
¦
+-- auto_factory.py           # Main factory orchestrator
+-- install_ffmpeg.py         # Auto ffmpeg installer
+-- setup.py                  # Project setup script
+-- setup.sh                  # Unix setup script
+-- requirements.txt
+-- docker-compose.yml
+-- Dockerfile
¦
+-- KHOI_DONG_APP.bat         # Windows: kh?i d?ng app
+-- CHAY_TU_DONG.bat          # Windows: ch?y t? d?ng
+-- VONG_LAP_TIEN_HOA.bat     # Windows: vòng l?p liên t?c
+-- KIEM_LOI_HE_THONG.bat     # Windows: ki?m tra l?i
```

---

## C?u hình

| Bi?n | M?c d?nh | Mô t? |
|------|---------|-------|
| `API_HOST` | `127.0.0.1` | Ð?a ch? bind REST API |
| `API_PORT` | `8100` | C?ng REST API |
| `WS_HOST` | `127.0.0.1` | WebSocket server bind |
| `WS_PORT` | `9222` | C?ng WebSocket |
| `POLL_INTERVAL` | `5` | Chu k? worker poll (giây) |
| `MAX_RETRIES` | `5` | S? l?n retry t?i da |
| `VIDEO_POLL_TIMEOUT` | `420` | Timeout video generation (giây) |
| `API_COOLDOWN` | `10` | Ngh? gi?a các API call (giây) |

---

## X? lý l?i ph? bi?n

| Tri?u ch?ng | Gi?i pháp |
|-------------|-----------|
| Extension hi?n "Agent disconnected" | Ch?y `python -m agent.main` |
| Extension hi?n "No token" | M? `labs.google/fx/tools/flow` và dang nh?p |
| `CAPTCHA_FAILED: NO_FLOW_TAB` | M? tab Google Flow |
| 403 `MODEL_ACCESS_DENIED` | Tier không d? — ki?m tra `/api/flow/credits`, h? model trong `models.json` |
| `media_id` b?t d?u b?ng `CAMS...` | Ch?y `/fk:fix-uuids` |
| Scene images không nh?t quán | Ki?m tra t?t c? refs có UUID `media_id` |
| Upscale "permission denied" | Yêu c?u tài kho?n `PAYGATE_TIER_TWO` |
| YouTube `invalidTags` | Tags vu?t 500 ký t? — gi?m b?t tags |
| ffmpeg not found | Ch?y `python install_ffmpeg.py` |

---

## License

MIT

---

## C?ng d?ng & H? tr?

<p align="center">
  <a href="https://www.facebook.com/groups/flowkit.flowboard.community">
    <img src="https://img.shields.io/badge/Join%20the%20Community-FlowKit%20%26%20Flowboard%20on%20Facebook-1877F2?style=for-the-badge&logo=facebook&logoColor=white" alt="Join the FlowKit & Flowboard Facebook Group" />
  </a>
</p>

C?ng d?ng chung cho **FlowKit** và **Flowboard**:
- Chia s? video và thumbnail dã t?o
- H?i dáp v? setup, l?i, tips
- Yêu c?u tính nang và báo bug

? **[facebook.com/groups/flowkit.flowboard.community](https://www.facebook.com/groups/flowkit.flowboard.community)**
