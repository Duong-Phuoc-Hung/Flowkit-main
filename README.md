<p align="center">
  <img src="docs/images/flowkit_banner.svg" width="720" alt="FLOW KIT" />
</p>

<p align="center">
  <a href="#license"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"/></a>
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python" alt="Python 3.10+"/>
  <img src="https://img.shields.io/badge/Next.js-15-black?logo=nextdotjs" alt="Next.js 15"/>
  <img src="https://img.shields.io/badge/Chrome-MV3-4285F4?logo=googlechrome" alt="Chrome MV3"/>
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/ffmpeg-required-007808" alt="ffmpeg"/>
</p>

# FLOW KIT

He thong san xuat video AI tu dong hoan chinh, tu y tuong den video YouTube.
Su dung **Google Flow API** thong qua Chrome extension lam cau noi xac thuc.

---

## Tong quan kien truc

`
+----------------------+   WebSocket (9222)   +--------------------------+
|  Python Agent        |<------------------->|  Chrome Extension         |
|  FastAPI + SQLite    |                     |  MV3 Service Worker       |
|  REST API :8100      |  -- commands -->    |  - Bat token ya29.*       |
|  Queue worker        |  <-- results --     |  - Giai reCAPTCHA v2      |
|  Post-process        |                     |  - Proxy Google Flow API  |
+----------------------+                     +--------------------------+
          |
          v
+----------------------+   HTTP (3000)        +--------------------------+
|  factory/            |<------------------->|  flowkit-web              |
|  Auto Pipeline       |                     |  Next.js 15 Dashboard     |
|  stage_1_script.py   |                     |  Tram 1: Nhap y tuong     |
|  stage_2_images.py   |                     |  Tram 2: Duyet kich ban   |
|  stage_3_videos.py   |                     |  Tram 3: Render anh/video |
|  stage_4_concat.py   |                     |  Tram 4: Hoan thanh       |
|  stage_5_upload.py   |                     |  Tram 5: YouTube upload   |
+----------------------+                     +--------------------------+
`

---

## Thanh phan du an

### 1. Chrome Extension (extension/)
- Bat token Google Flow (ya29.*) tu isandbox-pa.googleapis.com
- Tu dong giai reCAPTCHA v2
- Proxy toan bo Google Flow API ve local agent qua WebSocket
- Live Dashboard: request log, progress, trang thai ket noi

### 2. Python Agent (gent/)
- **FastAPI** REST API tren cong 8100
- **SQLite** (aiosqlite) luu projects, videos, scenes, characters, requests
- **Queue worker**: xu ly toi da 5 requests dong thoi, cooldown 10s
- **SDK domain model**: Project, Video, Scene, Character (queue + direct mode)
- **Post-processing**: ffmpeg trim/merge, mix nhac nen

### 3. Auto Factory (actory/)

Pipeline tu dong 5 giai doan:

| Stage | File | Mo ta |
|-------|------|-------|
| 1 | stage_1_script.py | AI sinh kich ban tu y tuong (Gemini) |
| 2 | stage_2_images.py | Sinh reference images + scene images |
| 3 | stage_3_videos.py | Render video AI (8s/scene) |
| 4 | stage_4_concat.py | ffmpeg concat + mix BGM |
| 5 | stage_5_upload.py | Upload YouTube tu dong |

### 4. Web Dashboard (lowkit-web/)

Next.js 15 app - giao dien dieu khien pipeline:

| Trang | Route | Chuc nang |
|-------|-------|-----------|
| Tram 1 | / | Nhap y tuong, dat ten du an, gui kich ban |
| Tram 2 | /tram-2 | Duyet va chinh sua kich ban AI sinh ra |
| Tram 2.5 | /tram-2-5 | Duyet anh reference truoc khi render |
| Tram 3 | /tram-3 | Theo doi render anh scene |
| Diep Vien | /diep-vien | Quan ly nhan vat/entities |
| Tram 4 | /tram-4 | Xem ket qua video hoan chinh |
| Tram 5 | /tram-5 | Upload YouTube |
| AI Phan Tich | /ai-phan-tich | Phan tich chat luong video bang AI |
| Cau Hinh | /cau-hinh | Cai dat he thong |

---

## Cai dat

### Yeu cau
- Python 3.10+
- Node.js 18+ (cho web dashboard)
- Google Chrome
- ffmpeg

### Buoc 1: Clone va cai ffmpeg

`ash
git clone https://github.com/Duong-Phuoc-Hung/Flowkit-main.git
cd Flowkit-main

# Auto-install ffmpeg (khuyen nghi)
python install_ffmpeg.py

# Hoac thu cong:
winget install Gyan.FFmpeg    # Windows
brew install ffmpeg           # macOS
sudo apt-get install -y ffmpeg # Linux
`

### Buoc 2: Cai Python dependencies

`ash
pip install -r requirements.txt
# Hoac tren Linux/macOS:
./setup.sh
`

### Buoc 3: Cau hinh moi truong

`ash
cp .env.example .env
`

| Bien | Mo ta |
|------|-------|
| GEMINI_API_KEY | Google Gemini API key (sinh kich ban) |
| ANTHROPIC_API_KEY | Claude API key (tuy chon) |
| API_PORT | Cong REST API (mac dinh: 8100) |
| API_COOLDOWN | Giay nghi giua API calls (mac dinh: 10) |

### Buoc 4: Cai Chrome Extension

1. Mo chrome://extensions
2. Bat **Developer mode**
3. Chon **Load unpacked** -> chon thu muc extension/
4. Mo [labs.google/fx/tools/flow](https://labs.google/fx/tools/flow) va dang nhap

### Buoc 5: Khoi dong Agent

`ash
python -m agent.main
`

Kiem tra ket noi:

`ash
curl http://127.0.0.1:8100/health
# {"status": "ok", "extension_connected": true}
`

### Buoc 6: Chay Web Dashboard (tuy chon)

`ash
cd flowkit-web
npm install
npm run dev
# Mo http://localhost:3000
`

---

## Chay nhanh tren Windows

| File | Chuc nang |
|------|-----------|
| KHOI_DONG_APP.bat | Khoi dong agent + web dashboard |
| CHAY_TU_DONG.bat | Chay auto factory pipeline |
| VONG_LAP_TIEN_HOA.bat | Vong lap tu dong lien tuc |
| KIEM_LOI_HE_THONG.bat | Kiem tra loi he thong |
| TAO_ICON_RA_MAN_HINH.bat | Tao shortcut desktop |

---

## Docker

`ash
docker-compose up -d
`

---

## Pipeline AI Skills

35+ workflow recipes trong skills/ cho Claude Code, Gemini CLI, Codex CLI:

### Pipeline co ban

| Skill | Mo ta |
|-------|-------|
| /fk:create-project | Tao project + entities + video + scenes |
| /fk:gen-refs | Sinh reference images cho tat ca entities |
| /fk:gen-images | Sinh scene images |
| /fk:gen-videos | Render video AI |
| /fk:concat | Ghep video + mix nhac |
| /fk:status | Dashboard trang thai project |
| /fk:pipeline | Orchestrator toan pipeline thong minh |

### Video nang cao

| Skill | Mo ta |
|-------|-------|
| /fk:gen-chain-videos | Video chaining (start+end frame transitions) |
| /fk:insert-scene | Chen scene moi (multi-angle, cutaway) |
| /fk:creative-mix | Phan tich + de xuat ky thuat toi uu |
| /fk:camera-guide | Huong dan goc may, chuyen dong, anh sang |

### TTS va Thuyet minh

| Skill | Mo ta |
|-------|-------|
| /fk:gen-tts-template | Tao voice template |
| /fk:gen-narrator | Sinh text thuyet minh + TTS |
| /fk:gen-text-overlays | Tao text overlay tu narrator |
| /fk:concat-fit-narrator | Cat video fit theo TTS roi ghep |
| /fk:gen-music | Sinh nhac nen qua Suno |

### YouTube

| Skill | Mo ta |
|-------|-------|
| /fk:youtube-seo | Sinh metadata SEO (title, description, tags) |
| /fk:brand-logo | Them logo/watermark kenh |
| /fk:thumbnail | Tao 4 thumbnail variants |
| /fk:youtube-upload | Upload tu dong voi lich dang |

### Tien ich

| Skill | Mo ta |
|-------|-------|
| /fk:monitor | Theo doi toan bo pipeline |
| /fk:doctor | Chan doan va sua loi |
| /fk:fix-uuids | Sua media_id sai (CAMS... -> UUID) |
| /fk:refresh-urls | Lam moi signed URLs het han |
| /fk:research | Kiem chung su kien truoc khi viet kich ban |
| /fk:review-video | Review chat luong video bang AI Vision |
| /fk:review-board | Web app xem nhanh toan bo scenes |

---

## Batch API

Gui nhieu requests cung luc (server tu throttle - max 5 dong thoi, cooldown 10s):

`ash
curl -X POST http://127.0.0.1:8100/api/requests/batch \
  -H "Content-Type: application/json" \
  -d '{"requests": [
    {"type": "GENERATE_IMAGE", "scene_id": "...", "project_id": "...", "video_id": "...", "orientation": "VERTICAL"}
  ]}'
`

Poll trang thai:

`ash
curl "http://127.0.0.1:8100/api/requests/batch-status?video_id=VID&type=GENERATE_IMAGE"
# {"total": 20, "pending": 10, "completed": 5, "done": false}
`

---

## API Reference

### CRUD Endpoints

| Resource | Create | List | Get | Update | Delete |
|----------|--------|------|-----|--------|--------|
| Project | POST /api/projects | GET /api/projects | GET /api/projects/{id} | PATCH /api/projects/{id} | DELETE /api/projects/{id} |
| Character | POST /api/characters | GET /api/characters | GET /api/characters/{id} | PATCH /api/characters/{id} | DELETE /api/characters/{id} |
| Video | POST /api/videos | GET /api/videos?project_id= | GET /api/videos/{id} | PATCH /api/videos/{id} | DELETE /api/videos/{id} |
| Scene | POST /api/scenes | GET /api/scenes?video_id= | GET /api/scenes/{id} | PATCH /api/scenes/{id} | DELETE /api/scenes/{id} |

### Endpoints dac biet

| Endpoint | Mo ta |
|----------|-------|
| GET /health | Trang thai server + extension |
| GET /api/flow/credits | Credits + tier nguoi dung |
| GET /api/materials | Danh sach materials (style anh) |
| POST /api/requests/batch | Gui nhieu requests cung luc |
| GET /api/requests/batch-status | Poll trang thai batch |

### Loai Request

| Type | Mo ta |
|------|-------|
| GENERATE_IMAGE | Sinh anh scene (bo qua neu da xong) |
| REGENERATE_IMAGE | Sinh lai anh scene |
| GENERATE_VIDEO | Render video tu anh |
| GENERATE_VIDEO_REFS | Render video tu reference images |
| UPSCALE_VIDEO | Upscale 4K (TIER_TWO only) |
| GENERATE_CHARACTER_IMAGE | Sinh reference image entity |
| REGENERATE_CHARACTER_IMAGE | Sinh lai reference image |

---

## Cau truc thu muc

`
flowkit-main/
├── agent/                    # Python FastAPI backend
│   ├── main.py               # FastAPI app + WebSocket server
│   ├── config.py             # Cau hinh (loads models.json)
│   ├── models.json           # Video/image model mappings
│   ├── materials.py          # Material/style system
│   ├── db/                   # SQLite schema + CRUD
│   ├── models/               # Pydantic models (API layer)
│   ├── api/                  # REST routes
│   ├── sdk/                  # Domain model SDK
│   │   ├── models/           # Project, Video, Scene, Character
│   │   └── services/         # OperationService, result_handler
│   ├── services/             # flow_client, headers, post_process
│   └── worker/               # Queue processor
│
├── factory/                  # Auto pipeline (5 stages)
│   ├── stage_1_script.py     # AI script generation (Gemini)
│   ├── stage_2_images.py     # Image generation
│   ├── stage_3_videos.py     # Video rendering
│   ├── stage_4_concat.py     # ffmpeg concat + BGM
│   └── stage_5_upload.py     # YouTube upload
│
├── flowkit-web/              # Next.js 15 web dashboard
│   └── src/app/              # Tram 1-5, ai-phan-tich, cau-hinh
│
├── extension/                # Chrome MV3 extension
│   ├── manifest.json
│   ├── background.js         # WebSocket bridge + token capture
│   ├── content.js            # reCAPTCHA solver
│   └── popup.html/js         # Live dashboard UI
│
├── skills/                   # 35+ AI agent workflow recipes
├── scripts/                  # Helper scripts
├── tools/                    # Utility tools
├── tests/                    # E2E tests
│
├── auto_factory.py           # Main factory orchestrator
├── install_ffmpeg.py         # Auto ffmpeg installer
├── setup.py                  # Project setup script
├── setup.sh                  # Unix setup script
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── KHOI_DONG_APP.bat
├── CHAY_TU_DONG.bat
├── VONG_LAP_TIEN_HOA.bat
└── KIEM_LOI_HE_THONG.bat
`

---

## Cau hinh

| Bien | Mac dinh | Mo ta |
|------|---------|-------|
| API_HOST | 127.0.0.1 | Dia chi bind REST API |
| API_PORT | 8100 | Cong REST API |
| WS_PORT | 9222 | Cong WebSocket |
| POLL_INTERVAL | 5 | Chu ky worker poll (giay) |
| MAX_RETRIES | 5 | So lan retry toi da |
| VIDEO_POLL_TIMEOUT | 420 | Timeout video generation (giay) |
| API_COOLDOWN | 10 | Nghi giua cac API call (giay) |

---

## Xu ly loi pho bien

| Trieu chung | Giai phap |
|-------------|-----------|
| Extension hien "Agent disconnected" | Chay python -m agent.main |
| Extension hien "No token" | Mo labs.google/fx/tools/flow va dang nhap |
| CAPTCHA_FAILED: NO_FLOW_TAB | Mo tab Google Flow |
| 403 MODEL_ACCESS_DENIED | Ha model trong models.json |
| media_id bat dau bang CAMS... | Chay /fk:fix-uuids |
| Upscale "permission denied" | Can tai khoan PAYGATE_TIER_TWO |
| YouTube invalidTags | Tags vuot 500 ky tu - giam bot |
| ffmpeg not found | Chay python install_ffmpeg.py |

---

## License

MIT

---

## Cong dong va Ho tro

<p align="center">
  <a href="https://www.facebook.com/groups/flowkit.flowboard.community">
    <img src="https://img.shields.io/badge/Join_the_Community-FlowKit_Flowboard-1877F2?style=for-the-badge&logo=facebook" alt="Facebook Group" />
  </a>
</p>

Cong dong chung cho **FlowKit** va **Flowboard** - chia se video, hoi dap, bao bug, yeu cau tinh nang.

**[facebook.com/groups/flowkit.flowboard.community](https://www.facebook.com/groups/flowkit.flowboard.community)**
