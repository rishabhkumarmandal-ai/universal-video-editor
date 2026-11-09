# Job format

`job.json` records the immutable source pointer, dimensions, declared output fps/duration and frame count. `plan.json` is editorial data, not a template containing old content. Start with `status: needs_editorial_plan`; set `status: ready` only after content/frame review.

```json
{
  "version": 1,
  "status": "ready",
  "width": 1080,
  "height": 1920,
  "fps": "30/1",
  "duration": 8,
  "summary": "Keep the opening on the speaker; show the described workflow; return for the real CTA.",
  "caption_y": 0.73,
  "highlightWords": ["workflow", "tools"],
  "scenes": [
    {"id":"intro","start":0,"end":2,"kind":"speaker","title":"Opening"},
    {"id":"workflow","start":2,"end":6,"kind":"diagram","theme":"light","title":"The actual process","nodes":[
      {"label":"Input","icon":"folder","at":2.2,"detail":"Use the script's term"},
      {"label":"Output","icon":"circle-check","at":3.2}
    ]},
    {"id":"close","start":6,"end":8,"kind":"speaker","title":"Closing"}
  ],
  "overlays":[
    {"start":0.3,"end":1.9,"label":"WORKFLOW","detail":"A concise script-supported label","icon":"code-xml","x":78,"y":215,"width":850,"height":158}
  ]
}
```

The numbers and terms above are schema examples, not preset timing/copy for the next video. Adapt geometry to the inspected frame and canvas; avoid blindly scaling the old close-up layout onto landscape or a different face position.

Scenes cover the whole output without overlaps/gaps; `speaker` uses the original footage. Full-screen scenes use `theme: light|dark`. Each node `at` is an absolute timeline time and must be inside its scene. Place it on the spoken word, not a default stagger when precise word timing exists. Overlay start/end are absolute too; x/y/width/height are canvas pixels and require actual-frame inspection. z-order: original picture → explanation clip → speaker overlay → captions. Avoid overlapping opaque overlays with explanation clips unless intentional.

Supported starter kinds:

- `cards`, `checklist`, `diagram`, `compare`: nodes `{label,detail?,icon,at}`.
- `orbit`: up to roughly three short node labels; timed sequential entrances and finite arc movement. For denser maps, author a dedicated composition rather than adding unreadable labels.
- `timeline`: nodes can set `widthPercent`; bars and a moving playhead explain a process, not invented measurements.
- `typing`: scene has `code` and optional `codeLabel`. Use actual supported commands when factual, or mark illustrative text clearly.
- `counter`: node has script-backed `value`, optional `from`, `suffix`, `duration`; non-numeric claims should use text instead. Avoid fake count-down starting numbers.
- `collage`: node `image` points to `assets/...`, copied from the job asset folder; use supplied/licensed images. Missing images are not a reason to invent a person or identity.

`transcript.json` is a list of `{start,end,text,words?}`. Optional word anchors are `{text,start,end}` and must match corrected text exactly; timestamps alone do not verify the wording. `captions.json` is generated groups with nested words. Machine transcripts remain separate.

`frame-plan.csv` uses output/conformed frame indices at the declared fps, end-exclusive scene bounds. Source-frame PTS is in `analysis/frame-metrics.csv`; variable-frame-rate source indices and output indices are not interchangeable. Label estimated word timing explicitly. The generator validates structural bounds; it cannot prove a fact, understand the speech or protect a face without visual review.
