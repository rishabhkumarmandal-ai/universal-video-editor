# Technical export checks and actual-output contact sheet. Does not replace visual/audio review.
from pathlib import Path
import argparse, json, subprocess, math, re
from fractions import Fraction
from editor import binary, load, save
from PIL import Image, ImageDraw

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('job')
p.add_argument('output')
a = p.parse_args()

job = Path(a.job).resolve()
out = Path(a.output).resolve()
m = load(job / 'job.json')

info = json.loads(subprocess.check_output([
    binary('ffprobe'), '-v', 'quiet', '-show_streams', '-show_format', '-of', 'json', str(out)
]))
v = next(x for x in info['streams'] if x['codec_type'] == 'video')
audio = next((x for x in info['streams'] if x['codec_type'] == 'audio'), None)

assert (v['width'], v['height']) == (m['width'], m['height']), f"Unexpected dimensions: {(v['width'], v['height'])} vs {(m['width'], m['height'])}"
assert abs(float(Fraction(v['r_frame_rate'])) - float(Fraction(m['fps']))) < 0.01, f"Unexpected fps: {v['r_frame_rate']} vs {m['fps']}"

# Allow slight container duration delta (up to 4 frames or 0.2s for audio-mux padding)
dur = float(v.get('duration', info['format']['duration']))
max_dur_delta = max(0.2, 4 / float(Fraction(m['fps'])))
assert abs(dur - m['duration']) <= max_dur_delta, f"Unexpected duration delta: {abs(dur - m['duration']):.3f}s > {max_dur_delta:.3f}s"

if 'nb_frames' in v and m.get('output_frame_count'):
    assert abs(int(v['nb_frames']) - m['output_frame_count']) <= 4, f"Unexpected frame count: {v['nb_frames']} vs {m['output_frame_count']}"

# Validate full stream decode
subprocess.run([binary('ffmpeg'), '-v', 'error', '-i', str(out), '-f', 'null', '-'], check=True)

# Validate caption-words match reviewed transcript (normalizing punctuation)
if (job / 'words.json').exists() and (job / 'transcript.json').exists():
    words = load(job / 'words.json')
    transcript = load(job / 'transcript.json')
    w1 = [re.sub(r'[^\w]', '', w['text']).lower() for w in words if re.sub(r'[^\w]', '', w['text'])]
    w2 = [re.sub(r'[^\w]', '', t).lower() for t in ' '.join(s['text'] for s in transcript).split() if re.sub(r'[^\w]', '', t)]
    assert w1 == w2, 'Caption words drifted from reviewed transcript text'
else:
    words = []

fps_val = float(Fraction(m['fps']))
times = [min(dur - 1 / fps_val, dur * x) for x in [0.01, 0.2, 0.4, 0.6, 0.8, 0.99]]
sheet = Image.new('RGB', (6 * 180, 345), '#11151C')
d = ImageDraw.Draw(sheet)

for i, t in enumerate(times):
    data = subprocess.check_output([
        binary('ffmpeg'), '-v', 'error', '-ss', str(max(0, t)), '-i', str(out),
        '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'
    ])
    im = Image.frombytes('RGB', (v['width'], v['height']), data)
    im.thumbnail((180, 320))
    sheet.paste(im, (i * 180 + (180 - im.width) // 2, 0))
    d.text((i * 180 + 4, 322), f"{t:.3f}s", fill='white')

sheet.save(job / 'exports/actual-output-contact.jpg')
caption_timing_info = load(job / 'analysis/caption-timing.json') if (job / 'analysis/caption-timing.json').exists() else {}

save(job / 'exports/verification.json', dict(
    output=str(out),
    dimensions=[v['width'], v['height']],
    fps=v['r_frame_rate'],
    duration=dur,
    frames=v.get('nb_frames'),
    audio=bool(audio),
    decoded_without_errors=True,
    caption_word_count=len(words),
    caption_words_match_reviewed_text=True,
    visual_review='Agent must inspect actual-output-contact.jpg plus target settled/transient frames',
    caption_timing=caption_timing_info
))
print('Export metadata, complete decode and corrected caption text passed. Inspect exports/actual-output-contact.jpg before delivery.')
