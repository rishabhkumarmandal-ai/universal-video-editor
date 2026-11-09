---
name: universal-video-editor
description: End-to-end video editor for talking-head reels and explainers. Analyzes source footage, extracts word-level Roman Hinglish transcripts, produces frame-by-frame editorial plans, assembles animated blue/black/grey HyperFrames motion graphics with solid headshot badges, renders broadcast-ready 1080x1920 MP4 video, and performs comprehensive audio/video QA.
---

# Universal Video Editor

A complete production pipeline for transforming raw video footage into polished, high-retention vertical reels (1080×1920). It enforces the accepted **blue/black/grey** design identity, **solid opaque headshot badges**, word-matched **Roman Hinglish captions**, dynamic **HyperFrames motion graphics**, and broadcast-grade audio normalization.

---

## 1. Core Visual Grammar & Design Language

The visual system is derived from the accepted production benchmark. These styling tokens must be strictly maintained across all scenes, overlays, and typography:

### Color Palette
| Token | Hex | Usage |
|---|---|---|
| **Primary Accent** | `#408CFF` | Vibrant brand blue for highlights, borders, active words, connectors |
| **Light Canvas Accent** | `#205AB0` | High-contrast deeper blue for text emphasis on light grey cards |
| **Canvas Dark / Black** | `#11151C` | Deep rich black background for dark scenes and overlay badges |
| **Light Canvas / Paper** | `#E9EDF3` | Crisp off-white/light grey background for conceptual explainers |
| **Card Surface Dark** | `#202734` | Midnight slate for code blocks, nested cards, and borders |
| **Text Primary (White)** | `#F5F7FA` | Off-white high legibility text on dark backgrounds |
| **Text Secondary (Dark)** | `#202734` | Charcoal high legibility text on light canvas |
| **Muted Grey** | `#AEB9C9` | Secondary labels, descriptions, and grid lines |
| **Solid Icon Tile** | `#D3DFF0` | **100% opaque** solid pastel blue/grey tile behind icons |

### Key Visual Rules
1. **Solid Headshot Badges (Never Translucent):**
   - Speaker overlays must have an **opaque background** (`#11151C`), `#408CFF` border, and a solid `#D3DFF0` icon tile with dark blue glyph.
   - **Never use semi-transparent backdrops** through which room clutter, background posters, or facial hair show.
   - Protect speaker face and eye lines by inspecting decoded frames before placing overlays.

2. **Roman Hinglish Captions:**
   - 2 to 3 words per caption chunk placed at lower torso (`y ≈ 73%`).
   - Font: **Poppins Bold** (72–80px at 1080×1920).
   - High legibility dark stroke on live video (`paint-order: stroke fill; -webkit-text-stroke: 5px #11151C`).
   - Active spoken word highlighted in real time (`#408CFF` on dark, `#205AB0` on light).
   - **Preserve authentic spoken Hinglish in Roman script** (e.g., *"par slot nahi"*, *"koi prompt nahi"*). Never machine-translate authentic conversational Hindi into English.

3. **Dynamic Motion Visuals & Direct Cuts:**
   - Alternate between direct camera footage and full-screen motion explanations (2.5s–5.0s per graphic).
   - Supported motion templates: UI cards, step checklists, architecture node diagrams, timeline bars, animated counters, typing code editors, and comparison layouts.
   - Entrance motion: crisp 0.3–0.4s staggers using GSAP (`power3.out` or `back.out(1.1)`), followed by comfortable read time.

---

## 2. Audio & Loudness Standards

1. **Original Voice Preservation:** Always keep the original speaker audio stream uncompressed (48 kHz, 16-bit stereo). Mute the live video track inside the browser compositor and mux high-quality audio directly.
2. **Loudness Compliance:**
   - Integrated Loudness: **-16.0 LUFS** (tolerance ±1.0 LUFS).
   - True Peak Ceiling: **≤ -1.0 dBTP** (target: -1.7 dBTP).
   - Optional music bed: soft, non-distracting instrumental groove mixed -18 dB to -24 dB below dialogue.
3. **Zero Audio Drift:** Verify cross-correlation offset between exported video audio and original uncompressed voice is **0.0 ms**.

---

## 3. End-to-End Execution Workflow

The editor operates across 6 deterministic stages:

```
[1. Doctor & Init] ➔ [2. Analyze & Transcribe] ➔ [3. Plan & Mockup] ➔ [4. HyperFrames Build] ➔ [5. Render] ➔ [6. Verify & QA]
```

### Stage 1: Environment Doctor & Job Isolation
```bash
# Verify binaries (ffmpeg, ffprobe, node, hyperframes, python packages)
.editing-tools/venv/bin/python skills/universal-video-editor/scripts/editor.py doctor

# Initialize job folder under jobs/<name>/ (leaves original source untouched)
.editing-tools/venv/bin/python skills/universal-video-editor/scripts/editor.py init /path/to/source.mov --out jobs/my-edit
```

### Stage 2: Audio Extraction, Video Metrics & Word-Level Transcription
```bash
# Decodes frames, measures RGB motion deltas, creates contact sheets, extracts 16kHz speech WAV
.editing-tools/venv/bin/python skills/universal-video-editor/scripts/editor.py analyze jobs/my-edit

# Transcribe with faster-whisper (auto-detects local turbo-int8 model if present)
.editing-tools/venv/bin/python skills/universal-video-editor/scripts/editor.py transcribe jobs/my-edit --language hi --model auto
```
- Review `transcript.machine.json` and output `transcript.json` with corrected Roman Hinglish wording.
- Run caption grouping to generate syllable/word-aligned caption blocks:
```bash
.editing-tools/venv/bin/python skills/universal-video-editor/scripts/editor.py captions jobs/my-edit
```

### Stage 3: Frame-by-Frame Editorial Planning
1. Formulate `plan.json` containing:
   - `scenes`: array of `{ id, start, end, kind, title, nodes }` covering 100% of duration without gaps or overlaps.
   - `overlays`: array of `{ start, end, label, detail, icon, x, y, width, height }` placed with exact inspected coordinates.
2. Generate timeline documents and CSVs:
```bash
.editing-tools/venv/bin/python skills/universal-video-editor/scripts/editor.py timeline jobs/my-edit
.editing-tools/venv/bin/python skills/universal-video-editor/scripts/editor.py validate jobs/my-edit
```
- Generates `second-by-second.csv`, `frame-plan.csv`, and `plan.md`.

### Stage 4: Composition Assembly & Browser Conformance
```bash
# Conforms source video to standard Rec.709 color and declared fps, extracts 48kHz voice WAV
.editing-tools/venv/bin/python skills/universal-video-editor/scripts/editor.py prepare jobs/my-edit

# Assembles self-contained HTML/CSS/GSAP composition inside jobs/my-edit/compositions/main/
.editing-tools/venv/bin/python skills/universal-video-editor/scripts/editor.py build jobs/my-edit
```

### Stage 5: Motion Graphic Rendering via HyperFrames
```bash
# Lint and validate HyperFrames contract
node tools/hyperframes.mjs lint jobs/my-edit/compositions/main
node tools/hyperframes.mjs validate jobs/my-edit/compositions/main --json

# Render output video frames (using source fps and headless browser)
node tools/hyperframes.mjs render jobs/my-edit/compositions/main --workers 1 --fps 30 -o jobs/my-edit/working/picture.mp4

# Mux picture with normalized 48kHz audio mix
ffmpeg -y -v warning -i jobs/my-edit/working/picture.mp4 -i jobs/my-edit/working/voice.wav -c:v copy -c:a aac -b:a 256k -shortest jobs/my-edit/exports/final.mp4
```

### Stage 6: Technical QA & Export Verification
Run automated technical checks:
```bash
.editing-tools/venv/bin/python skills/universal-video-editor/scripts/verify_export.py jobs/my-edit jobs/my-edit/exports/final.mp4
```
Checks performed:
- [x] Exact output resolution (1080×1920) and declared fps.
- [x] Full stream decode pass (100% video/audio frames decoded with 0 errors).
- [x] 100% word-level coverage against reviewed transcript.
- [x] Contact sheet generated at `exports/actual-output-contact.jpg`.

---

## 4. HyperFrames Authoring Contract Rules

When customizing or authoring `index.html` compositions:
- **Root Element:** `<div id="root" data-composition-id="main" data-start="0" data-duration="DUR" data-width="1080" data-height="1920" data-fps="30">`.
- **StaticGuard Rule:** Do NOT wrap `<video>` inside a timed container div that also has `data-start`. The `<video>` element itself must carry timeline attributes (`data-start`, `data-duration`, `data-track-index`).
- **Deterministic GSAP:** Timelines must be initialized with `{ paused: true }` and registered on `window.__timelines = { main: tl }`.
- **Layering Order (Z-Index):**
  * `z-index: 0` – Live speaker camera video
  * `z-index: 10` – Full-screen motion graphic scenes
  * `z-index: 20` – Solid headshot badges and speaker overlays
  * `z-index: 30` – Roman Hinglish captions

---

## 5. Artifact Delivery Checklist

Upon completion of every edit, provide:
1. **Master Video:** `exports/<name>-FINAL.mp4` (1080×1920, H.264/AAC, broadcast loudness).
2. **Subtitles:** `exports/<name>-subtitles.srt` (time-stamped word-grouped SRT).
3. **Verified Contact Sheet:** `exports/actual-output-contact.jpg`.
4. **Complete Transcripts:** `TRANSCRIPT.md` and `transcription-by-second.csv`.
5. **Editorial Plan:** `EDIT-PLAN.md` and `frame-plan.csv`.
6. **QA Report:** `exports/verification.json` confirming decode, audio sync, and word match.
