# OpenDesign / HyperFrames workflow

Primary reference: https://github.com/nexu-io/open-design/tree/main/design-templates/hyperframes
Authoring contract: https://github.com/nexu-io/open-design/blob/main/design-templates/hyperframes/SKILL.md
Motion guidance: https://github.com/nexu-io/open-design/blob/main/design-templates/hyperframes/references/motion-principles.md
Standalone implementation: https://github.com/heygen-com/hyperframes

This repo uses the standalone `hyperframes` npm package, pinned in package-lock.json, plus GSAP. The full OpenDesign app is **not** required. `@hyperframes/cli` is not the package name. Node >=22 is needed for the pinned CLI; OpenDesign's own workspace may require a different Node/pnpm version. Do not install a whole app to solve a local composition task.

## In an existing OpenDesign project

If OD_PROJECT_DIR / OD_PROJECT_ID / OD_BIN / OD_NODE_BIN are supplied by OpenDesign, use its scaffold and render dispatch instead of inventing a daemon configuration. Follow the current upstream contract:

1. Create a hidden composition cache under that project.
2. Run the supplied `media scaffold --project ... --composition-dir ...`.
3. Apply the approved DESIGN.md palette/typography and author the script-relevant visuals.
4. Run lint/validate/inspect using the environment's HyperFrames binary.
5. Dispatch `media generate --project ... --surface video --model hyperframes-html --composition-dir ... --output ...` through the daemon; wait on the returned task ID with its documented short-poll command.

Use actual returned environment variables and tool schema. A GitHub link alone does not mean a live OpenDesign project exists. Never claim the local fallback export was rendered by OD.

## Standalone local workflow (tested here)

At this repository root:

```bash
npm ci
node tools/hyperframes.mjs lint JOB/compositions/main
node tools/hyperframes.mjs validate JOB/compositions/main --json
node tools/hyperframes.mjs inspect JOB/compositions/main --json
node tools/hyperframes.mjs snapshot JOB/compositions/main --at 1,3,5 --no-end
node tools/hyperframes.mjs render JOB/compositions/main --workers 1 --fps 30 -o JOB/exports/final.mp4
```

Use source/job fps, not the example 30 when different. CLI flags can change: check installed `--help` before using new operations. Wrapper disables anonymous CLI telemetry and discovers this workspace's retained FFmpeg binaries; elsewhere use system binaries. Chrome can be found automatically or through HYPERFRAMES_BROWSER_PATH. Ordinary system Chrome uses screenshot capture, which is valid but slower than headless-shell's optimized path. Do not install cloud credentials or paid services as a fallback.

All media and scripts for generated compositions are local. Root `index.html` contains the visible composition div (not a hidden template), with explicit width, height, duration, fps and `data-composition-id`. Timed clips use start + duration + track index. CSS z-index controls visual layering. Original video is muted; original voice is a separate audio clip. Do not nest timed videos under timed divs. Never imperatively play/seek media in animation callbacks.

Each GSAP timeline is paused and synchronously registered in `window.__timelines`. Use deterministic motion and finite repeats. Build the settled layout first, then entrance motion. Do not use independent tweens on the same transform property at overlapping times: orbit position and entrance scale/opacity must be separate properties/wrappers. The bundled template follows this split.

## Verification and adaptation

The templates are starters, not a guarantee of polished layouts for arbitrary text. Inspect long labels, portrait/landscape sizing, collage images, orbit bounds and caption clearance. Fix the generated HTML or improve the template based on observed problems. Do not paper over missing content or assets with a blank scene.

For the creator's direct speaker/cutaway rhythm, prefer individual full-screen compositions conformed by an outer video timeline. For a multi-scene graphic composition, follow explicit transition choreography. There is no need to copy upstream generic colour choices or mix orange into the accepted brand.

If the preferred engine fails, diagnose once, make a targeted repair and retry. If still blocked, explain the limitation and use a verified local FFmpeg/Pillow alternative when available. The original accepted Stackvideo was made with that local compositor in this workspace; it is an example, not a portable universal renderer bundled here.

Before delivery inspect actual MP4 frames, decode all frames, check duration/rate, verify caption words match the corrected transcript, inspect first/last frames and the CTA, and measure audio. Audio offset checks do not establish perfect caption timing. Never report a render as complete because HTML lint passed.
