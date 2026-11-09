---
name: universal-video-editor
description: Analyze, transcribe, plan, and edit user-supplied videos into broadcast-ready reels or explainers using the approved blue/black/grey style, Roman Hinglish word-timed captions, solid opaque headshot badges, and editable HyperFrames HTML/CSS/GSAP motion graphics.
---

# Universal Video Editor — Complete Standalone Skill Specification

A unified production pipeline for turning raw footage into finished, high-retention vertical reels (1080×1920 @ 30fps). This specification incorporates the approved **blue/black/grey** aesthetic, **solid opaque headshot badges**, word-matched **Roman Hinglish captions**, dynamic **HyperFrames motion graphics**, and broadcast audio standards.

---

## 1. Design Grammar & Accepted Aesthetics

### 1.1 Color Tokens
- **Primary Brand Blue (`#408CFF`):** Main accent for glowing badges, active words, timeline progress bars, and node connectors.
- **Light Surface Accent (`#205AB0`):** High-contrast deep blue used for text and icon emphasis on light backgrounds.
- **Deep Slate Black (`#11151C`):** 100% opaque background for dark scenes, live-speaker overlay cards, and letterboxing.
- **Light Slate Paper (`#E9EDF3`):** Clean, crisp background for diagram and architecture explainers.
- **Midnight Card Dark (`#202734`):** Secondary card surface for code blocks, checklist backgrounds, and borders.
- **Text White (`#F5F7FA`):** High-contrast headline and body text on dark canvas.
- **Text Dark Charcoal (`#202734`):** Crisp headline text on light canvas.
- **Muted Grey (`#AEB9C9`):** Subtitles, meta-tags, and subtle grid lines.
- **Solid Icon Tile (`#D3DFF0`):** **100% opaque** solid pastel blue-grey icon tile. **Never translucent.**

### 1.2 Typography & Badges
- **Font:** Poppins Bold (`Poppins-Bold.ttf`).
- **Captions:**
  - Placed at lower torso (`y ≈ 73%`).
  - Size: 72–80px at 1080×1920.
  - Chunk size: 2 to 3 words per line.
  - Live footage outline: `paint-order: stroke fill; -webkit-text-stroke: 5px #11151C; color: #F5F7FA`.
  - Word tracking: Real-time active word highlight (`#408CFF` on dark canvas, `#205AB0` on light canvas).
  - Language: **Roman Hinglish**. Maintain the natural spoken Hindi/English vocabulary verbatim (e.g. *"par slot nahi"*, *"koi prompt nahi"*). Never machine-translate into formal English.
- **Headshot Badges:**
  - Opaque `#11151C` background with `#408CFF` border.
  - Left-aligned solid `#D3DFF0` icon tile (112×112px) housing a 72×72px dark blue SVG glyph.
  - Clear of speaker face, mouth, and eye-line based on actual inspected frames.

### 1.3 Motion Grammar
- **Pacing:** Dynamic rhythm alternating between direct speaker cuts and full-screen motion graphic explainers (2.5s–5.0s per graphic).
- **GSAP Timings:** 0.3s–0.4s entrance staggers (`power3.out` or `back.out(1.1)`), followed by steady hold for legibility.
- **Graphic Families:**
  - `cards`: Structured information tiles with icons and descriptions.
  - `checklist`: Animated task verification with green/blue checks.
  - `diagram`: Architecture nodes with glowing SVG connectors.
  - `timeline`: Linear milestone bars with animated playhead.
  - `typing`: Monospace code editor with typing cursor effect.
  - `counter`: Tabular-numeral stat counters with smooth easing.

---

## 2. Audio Engineering Standards

1. **Dialogue Clarity:** The original speaker voice must remain uncompressed and untouched by aggressive filtering (48 kHz, 16-bit stereo).
2. **Loudness Compliance:**
   - Integrated Loudness: **-16.0 LUFS** (±1.0 LUFS target).
   - True Peak Maximum: **≤ -1.0 dBTP** (target: -1.70 dBTP).
3. **Audio Bed & SFX:** Subtle background instrumental groove mixed -18 dB to -24 dB below dialogue; gentle UI clicks and swooshes aligned to visual entrance cues.
4. **Synchronization Verification:** Compute cross-correlation between the final export's audio track and original voice to confirm **0.0 ms audio drift**.

---

## 3. The 6-Stage Production Workflow

### Stage 1: Environment Diagnostics & Job Isolation
```bash
# Verify environment dependencies
.editing-tools/venv/bin/python skills/universal-video-editor/scripts/editor.py doctor

# Initialize job directory
.editing-tools/venv/bin/python skills/universal-video-editor/scripts/editor.py init /path/to/source.mov --out jobs/<name>
```

### Stage 2: Content Analysis & Word-Level Transcription
```bash
# Decodes frames, logs RGB delta metrics, extracts speech WAV
.editing-tools/venv/bin/python skills/universal-video-editor/scripts/editor.py analyze jobs/<name>

# Word-accurate Hinglish transcription using faster-whisper
.editing-tools/venv/bin/python skills/universal-video-editor/scripts/editor.py transcribe jobs/<name> --language hi --model auto

# Format 2-3 word caption blocks and export SRT
.editing-tools/venv/bin/python skills/universal-video-editor/scripts/editor.py captions jobs/<name>
```

### Stage 3: Frame-by-Frame Editorial Planning
1. Write `plan.json` covering 100% of the video duration.
2. Generate CSV timelines and markdown breakdowns:
```bash
.editing-tools/venv/bin/python skills/universal-video-editor/scripts/editor.py timeline jobs/<name>
.editing-tools/venv/bin/python skills/universal-video-editor/scripts/editor.py validate jobs/<name>
```

### Stage 4: Composition Assembly & Browser Conformance
```bash
# Conform source to Rec.709 color and output framerate
.editing-tools/venv/bin/python skills/universal-video-editor/scripts/editor.py prepare jobs/<name>

# Assemble standalone HTML/CSS/GSAP composition
.editing-tools/venv/bin/python skills/universal-video-editor/scripts/editor.py build jobs/<name>
```

### Stage 5: HyperFrames Rendering & Muxing
```bash
# Render visual composition at source fps
node tools/hyperframes.mjs render jobs/<name>/compositions/main --workers 1 --fps 30 -o jobs/<name>/working/picture.mp4

# Mux picture with normalized 48kHz audio mix
ffmpeg -y -v warning -i jobs/<name>/working/picture.mp4 -i jobs/<name>/working/voice.wav -c:v copy -c:a aac -b:a 256k -shortest jobs/<name>/exports/final.mp4
```

### Stage 6: Technical QA & Verification
```bash
.editing-tools/venv/bin/python skills/universal-video-editor/scripts/verify_export.py jobs/<name> jobs/<name>/exports/final.mp4
```

---

## 4. HyperFrames Authoring Contract Rules

- **Root Element:** `<div id="root" data-composition-id="main" data-start="0" data-duration="DUR" data-width="1080" data-height="1920" data-fps="30">`.
- **StaticGuard Rule:** Never nest `<video>` inside a timed container div that has `data-start`. The `<video>` element itself must directly carry `data-start="0"` and `data-track-index="0"`.
- **GSAP Registry:** Timelines must start paused: `const tl = gsap.timeline({ paused: true });` and be exposed on `window.__timelines = { main: tl };`.
- **Z-Index Layer Hierarchy:**
  - `0`: Live camera footage
  - `10`: Full-screen motion graphics
  - `20`: Solid speaker badges and overlays
  - `30`: Word-highlighted captions

---

## 5. Standard Deliverables Package

Every completed edit must produce:
1. `exports/<name>-FINAL.mp4`: Broadcast-ready 1080×1920 video.
2. `exports/<name>-subtitles.srt`: Accurate Roman Hinglish SRT subtitle file.
3. `exports/actual-output-contact.jpg`: Contact sheet of actual rendered frames.
4. `exports/verification.json`: Automated decode and word-coverage report.
5. `TRANSCRIPT.md` & `transcription-by-second.csv`: Complete speech transcript.
6. `EDIT-PLAN.md` & `frame-plan.csv`: Comprehensive editorial and scene plan.
