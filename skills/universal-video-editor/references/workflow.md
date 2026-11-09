# Job workflow and helper commands

Resolve the skill directory and repo from their real filesystem paths. Installed skill symlinks resolve back to this repository. On another machine, install Python requirements and run `npm ci` at the repo root. FFmpeg/FFprobe can be on PATH or configured through FFMPEG_BIN / FFPROBE_BIN. This workspace also has retained `.editing-tools` binaries and Python environment; `doctor` detects those without shell aliases.

```bash
python3 SKILL/scripts/editor.py doctor
python3 SKILL/scripts/editor.py init /path/to/source.mov --out jobs/my-edit
python3 SKILL/scripts/editor.py analyze jobs/my-edit
python3 SKILL/scripts/editor.py transcribe jobs/my-edit --language hi --model small
```

Use the repository's `.editing-tools/venv/bin/python` here if system Python lacks media packages. Choose a stronger ASR model/backend when available and justified. A small CPU model is a portable starting point, not proof of accurate Hinglish recognition. Transcription reads PCM through numpy rather than passing filenames into faster-whisper, avoiding the demonstrated PyAV metadata_errors incompatibility. Low-probability words are review cues, not a complete detector of hallucination.

`init` creates an isolated manifest and blank editorial plan, not a ready-made story. `analyze` decodes frames into `analysis/frame-metrics.csv`, metadata, cut candidates and contact sheets. It does not claim a semantic cut detector or individual-frame visual review. Inspect target frames before placing overlays. For large sources sample appropriately; do not retain thousands of full-resolution PNGs unnecessarily.

`transcribe` writes raw machine JSON and a readable draft, never overwriting `transcript.json`. The agent reviews the wording and supplies `transcript.json` as segments `{start,end,text,words?}`. User corrections are authoritative. Words, when supplied, use `{text,start,end}`; otherwise caption timings are explicitly estimated inside phrase anchors. A different backend or a forced aligner can replace the estimates without changing corrected text.

```bash
python3 SKILL/scripts/editor.py captions jobs/my-edit
# Agent writes meaningful scenes/overlays into plan.json using transcript + frame evidence.
python3 SKILL/scripts/editor.py timeline jobs/my-edit
python3 SKILL/scripts/editor.py validate jobs/my-edit
python3 SKILL/scripts/editor.py prepare jobs/my-edit
python3 SKILL/scripts/editor.py build jobs/my-edit
```

`prepare` creates a browser-compatible working video and separate original-voice WAV. HLG/PQ inputs get an explicit Rec.709 conversion; originals stay immutable. It conforms a working copy to the manifest's declared output fps; do not claim exact preservation of variable-frame-rate timestamps after conforming. Analysis CSV retains source PTS.

`build` copies media/assets into `compositions/main/` and generates editable HyperFrames HTML. It requires a reviewed plan and transcript; it does not guess a polished plan from keywords. Semantic editing is the agent's responsibility. Files are self-contained, with local GSAP/font/icons; no CDN is needed for playback. It supports common composition forms; tailor the HTML for new visual ideas instead of forcing every idea into one card form.

Then lint/validate/preview/render using `references/hyperframes.md`. Add optional SFX/music only if actually available and licensed. The starter composition preserves original voice; it does not silently invent a soundtrack or normalize multiple times. Measure the final mix and adjust as needed.

Expected artifacts: `transcript.md`, `transcript.json`, `plan.md`, `plan.json`, `second-by-second.csv`, `frame-plan.csv`, `captions.srt`, `captions.json`, `compositions/main/index.html`, `exports/final.mp4`, and verification notes. Delivery links point at real finished artifacts, not a promised path.

For colour-only revisions, freeze caption/scene/event timing, change palette and solid fills, render picture, then copy the approved audio stream. Verify duration, fps/frame count, decode, caption wording, audio offset, and representative actual exported frames. If speech changes, reflow downstream timing deliberately.

After render, run `python3 SKILL/scripts/verify_export.py JOB JOB/exports/final.mp4`. It checks dimensions, declared rate/duration, complete decode, corrected caption-word coverage and saves actual exported-frame contact images. Inspect them and targeted transients; technical checks alone do not prove appearance or caption semantics.
