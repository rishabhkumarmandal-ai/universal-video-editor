# Universal video editing skill repository

This folder is now the reusable editing workspace for the user's approved **blue / black / grey** video style. The original footage, reference videos, completed Stackvideo edits and tools remain in place. Git ignores those private media/runtime folders; the reusable skill, templates, helper scripts and compact style references are versionable.

The skill automatically starts **analysis → transcript → edit plan → editing → render → verification** when a new video is supplied for editing. It presents transcript and plan artifacts, then continues without routine approval pauses. Explicit transcript-only, plan-only or other limits always win. Unclear speech that changes meaning is clarified rather than invented.

The default combines solid headshot icon badges and short Roman Hinglish captions with clean UI cutaways (ref-1) and conceptual motion / diagrams / timelines / collages (ref-3). The accepted final output is the visual baseline. New footage gets new content, timing and geometry; the skill does not reuse Stackvideo's script, duration or CTA.

## Use in Codex

The skill is `skills/universal-video-editor/SKILL.md`, with automatic discovery enabled. A local installation is linked from `~/.codex/skills/universal-video-editor`. Skill discovery may refresh in a new Codex conversation. `AGENTS.md` also routes video editing tasks in this directory directly to it.

Give Codex a video path and say “edit this video”; in this established workflow a new video supplied for editing is enough. Explicit invocation also works:

> Use $universal-video-editor on `/path/to/my-video.mov`. Give me the transcript and plan, then finish the edit.

## Tools and project layout

- `skills/universal-video-editor/`: discoverable instructions, reference rules, brand assets, HyperFrames starter and Python job utilities.
- `tools/hyperframes.mjs`: pinned local HyperFrames CLI wrapper; no OpenDesign app installation needed.
- `examples/`: data-only examples and provenance, not private source videos.
- `jobs/<name>/`: new isolated projects, ignored by Git.
- Existing `.editing-tools`, `stackvideo-edit`, `reference-videos`, `local-edit`, `blue-grey-edit`: retained local history/runtime, ignored by Git. Never run the legacy hardcoded script on new footage.

On another machine: Python 3.10+, Node 22+, FFmpeg/FFprobe, `pip install -r requirements.txt`, and `npm ci`. ASR may download the selected model on first use. Here the retained `.editing-tools/venv` and static FFmpeg binaries are already available. Do not commit models, node_modules, credentials or original/client footage.

```bash
.editing-tools/venv/bin/python skills/universal-video-editor/scripts/editor.py doctor
.editing-tools/venv/bin/python skills/universal-video-editor/scripts/editor.py init /path/to/video.mov --out jobs/new-edit
```

The agent uses the helper commands documented in the skill to analyze frames, transcribe, review wording, write a content-specific plan, build editable HTML/CSS/GSAP, render and verify. This is an agent workflow with deterministic utilities, not a one-command algorithm that guesses editorial meaning from audio.

## Repository status

Local Git repository only. No remote repository is created and nothing is pushed or published. The reusable files exclude large private media by default. The approved full video remains at `stackvideo-edit/Stackvideo-BLUE-BLACK-GREY-FINAL.mp4`.

Read `THIRD_PARTY_NOTICES.md` before redistributing assets. Reference contact sheets are private style evidence; no redistribution rights to their footage/creators are asserted.
