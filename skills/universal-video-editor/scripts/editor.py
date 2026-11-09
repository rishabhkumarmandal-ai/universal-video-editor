#!/usr/bin/env python3
"""Reusable job utilities. Semantic transcript review and visual planning belong to the agent."""
from pathlib import Path
import argparse,csv,hashlib,json,math,os,re,shutil,subprocess,sys
from fractions import Fraction
SKILL=Path(__file__).resolve().parents[1];REPO=SKILL.parents[1]
def load(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def binary(name):
 candidates=[os.environ.get(name.upper()+'_BIN'),shutil.which(name)]
 if name=='ffmpeg':candidates += [str(REPO/'.editing-tools/node_modules/ffmpeg-static/ffmpeg')]
 if name=='ffprobe':candidates += [str(REPO/'.editing-tools/node_modules/ffprobe-static/bin/linux/x64/ffprobe')]
 for x in candidates:
  if x and Path(x).is_file():return str(Path(x).resolve())
 raise RuntimeError(f'{name} missing: install it or set {name.upper()}_BIN')
def probe(source):return json.loads(subprocess.check_output([binary('ffprobe'),'-v','quiet','-show_streams','-show_format','-of','json',str(source)]))
def manifest(job):return load(Path(job)/'job.json')
def write_transcript(job,segments,raw=False):
 name='transcript.machine.md' if raw else 'transcript.md'
 with open(job/name,'w') as o:
  o.write('# Transcript '+('— machine draft; review required' if raw else '— reviewed wording')+'\n\n')
  for s in segments:o.write(f"**{s['start']:.3f}–{s['end']:.3f}s** {s['text']}\n\n")
def cmd_doctor(a):
 import importlib.util
 venv_py = REPO/'.editing-tools/venv/bin/python'
 print(json.dumps(dict(python=sys.executable,venv_python=str(venv_py) if venv_py.is_file() else None,ffmpeg=binary('ffmpeg'),ffprobe=binary('ffprobe'),node=shutil.which('node'),packages={x:bool(importlib.util.find_spec(x)) for x in ['av','PIL','numpy','faster_whisper']},hyperframes=str(REPO/'node_modules/.bin/hyperframes') if (REPO/'node_modules/.bin/hyperframes').exists() else None),indent=2))
def cmd_init(a):
 source=Path(a.source).expanduser().resolve();job=Path(a.job).expanduser().resolve()
 if not source.is_file():raise ValueError('Source file does not exist')
 if (job/'job.json').exists():raise ValueError('Existing job: use another output folder; no automatic overwrite')
 p=probe(source);v=next(s for s in p['streams'] if s['codec_type']=='video');rate=v.get('r_frame_rate') or v['avg_frame_rate'];fps=Fraction(rate)
 if fps<=0 or fps>240:rate=v['avg_frame_rate'];fps=Fraction(rate)
 duration=float(v.get('duration') or p['format']['duration']);n=round(duration*float(fps))
 for f in ['analysis','assets','compositions','exports','working']:(job/f).mkdir(parents=True,exist_ok=True)
 save(job/'source-probe.json',p);save(job/'job.json',dict(version=1,source=str(source),source_size=source.stat().st_size,width=int(v['width']),height=int(v['height']),fps=rate,duration=duration,output_frame_count=n,colour_transfer=v.get('color_transfer'),has_audio=any(s['codec_type']=='audio' for s in p['streams']),workflow='transcribe-plan-edit',style='approved-blue-black-grey'))
 save(job/'plan.json',dict(version=1,status='needs_editorial_plan',width=int(v['width']),height=int(v['height']),fps=rate,duration=duration,caption_y=.73,scenes=[],overlays=[]))
 print(job)
def cmd_analyze(a):
 import av,numpy as np
 from PIL import Image,ImageDraw
 job=Path(a.job);m=manifest(job);c=av.open(m['source']);v=c.streams.video[0];last=None;rows=[];thumbs=[];nextt=0
 for i,f in enumerate(c.decode(video=0)):
  t=float(f.time) if f.time is not None else i/float(Fraction(m['fps']));small=f.reformat(width=72,height=128,format='rgb24').to_ndarray().astype(np.float32)
  delta=0 if last is None else float(np.abs(small-last).mean());last=small;rows.append((i,t,delta))
  if t+1e-6>=nextt:
   im=f.to_image();im.thumbnail((180,320));thumbs.append((t,i,im));nextt+=a.interval
 with open(job/'analysis/frame-metrics.csv','w') as o:
  w=csv.writer(o);w.writerow(['frame','pts_seconds','mean_rgb_change']);w.writerows(rows)
 for p in range(0,len(thumbs),20):
  sub=thumbs[p:p+20];sheet=Image.new('RGB',(900,math.ceil(len(sub)/5)*345),'#11151C');d=ImageDraw.Draw(sheet)
  for j,(t,i,im) in enumerate(sub):
   x=j%5*180;y=j//5*345;sheet.paste(im,(x+(180-im.width)//2,y));d.text((x+3,y+322),f'{t:.3f}s f{i}',fill='white')
  sheet.save(job/f'analysis/contact-{p//20+1}.jpg')
 save(job/'analysis/summary.json',dict(decoded_frames=len(rows),last_pts=rows[-1][1],candidate_cuts=sorted(rows,key=lambda x:x[2],reverse=True)[:30],visual_review='Pending agent inspection; metrics alone are not semantic review'))
 if m.get('has_audio',True):
  subprocess.run([binary('ffmpeg'),'-v','error','-y','-i',m['source'],'-vn','-ac','1','-ar','16000',str(job/'analysis/speech.wav')],check=True)
 else:
  import wave
  with wave.open(str(job/'analysis/speech.wav'),'wb') as audio:
   audio.setnchannels(1);audio.setsampwidth(2);audio.setframerate(16000);audio.writeframes(bytes(round(m['duration']*16000)*2))
 print(f'{len(rows)} frames measured; {len(thumbs)} contact samples; speech WAV ready')
def cmd_transcribe(a):
 import numpy as np,wave
 from faster_whisper import WhisperModel
 job=Path(a.job);wav=job/'analysis/speech.wav'
 if not wav.exists():raise ValueError('Run analyze first')
 with wave.open(str(wav)) as f:
  assert f.getnchannels()==1 and f.getframerate()==16000 and f.getsampwidth()==2
  audio=np.frombuffer(f.readframes(f.getnframes()),np.int16).astype(np.float32)/32768
 if not manifest(job).get('has_audio',True):
  save(job/'transcript.machine.json',[]);write_transcript(job,[],True);print('No source audio; no speech invented');return
 if a.model in ['turbo', 'auto']:
  local_turbo = REPO/'.editing-tools/models/turbo-int8'
  model_id = str(local_turbo) if local_turbo.is_dir() else ('turbo' if a.model=='turbo' else 'small')
 else:
  model_id = a.model
 model=WhisperModel(model_id,device=a.device,compute_type='int8' if a.device=='cpu' else 'float16',cpu_threads=a.threads)
 segs,info=model.transcribe(audio,language=None if a.language=='auto' else a.language,word_timestamps=True,beam_size=3,vad_filter=True)
 result=[]
 for s in segs:
  row=dict(start=s.start,end=s.end,text=s.text.strip(),words=[dict(text=w.word.strip(),start=w.start,end=w.end,probability=float(w.probability),needs_review=bool(w.probability<.65)) for w in s.words or []]);result.append(row)
  save(job/'transcript.machine.json',result);print(f'{s.start:.2f}–{s.end:.2f}: {s.text}',flush=True)
 save(job/'transcript.machine.json',result);write_transcript(job,result,True);save(job/'analysis/asr-info.json',dict(model=a.model,language=info.language,language_probability=float(info.language_probability),review_required=True))
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
def cmd_captions(a):
 job=Path(a.job);segments=load(job/'transcript.json');words=[];estimated=False
 for s in segments:
  if not (0<=s['start']<s['end']<=manifest(job)['duration']+.1):raise ValueError('Bad transcript span')
  if s.get('words'):
   if ' '.join(w['text'] for w in s['words']).split()!=s['text'].split():raise ValueError('Word timestamps disagree with corrected text')
   words.extend(s['words'])
  else:
   estimated=True;ts=s['text'].split();weights=[max(1,len(re.findall('[aeiouAEIOU]+',t))) for t in ts];cur=s['start']
   for t,w in zip(ts,weights):
    end=cur+(s['end']-s['start'])*w/sum(weights);words.append(dict(text=t,start=cur,end=end));cur=end
 if any(words[i]['start']<words[i-1]['start'] for i in range(1,len(words))):raise ValueError('Words not in timeline order')
 groups=[];i=0
 while i<len(words):
  n=min(3,len(words)-i)
  for k in range(1,n):
   if words[i+k]['text'].lower() in ['par','koi','not','never']:n=k;break
  for k in range(n-1):
   if words[i+k]['text'].endswith(('.',',','!','?')):n=k+1;break
  for k in range(1,n):
   if words[i+k]['start']-words[i+k-1]['end']>.2:n=k;break
  ws=words[i:i+n];groups.append(dict(start=ws[0]['start'],end=ws[-1]['end'],text=' '.join(w['text'] for w in ws),words=ws));i+=n
 save(job/'words.json',words);save(job/'captions.json',groups);save(job/'analysis/caption-timing.json',dict(method='estimated syllable weighting inside reviewed phrases' if estimated else 'provided word anchors',manually_verified=False))
 with open(job/'captions.srt','w') as o:
  for j,g in enumerate(groups):o.write(f"{j+1}\n{stamp(g['start'])} --> {stamp(g['end'])}\n{g['text']}\n\n")
 write_transcript(job,segments);print(f'{len(words)} corrected words / {len(groups)} caption groups; estimated={estimated}')
def get_span(x):
 return x.get('start', x.get('start_sec', 0.0)), x.get('end', x.get('end_sec', 0.0))
def validate(job):
 p=load(job/'plan.json');m=manifest(job);s=p['scenes'];duration=m['duration'];errors=[]
 if p.get('status')=='needs_editorial_plan' or not s:errors.append('Agent must create an editorial plan')
 cursor=0
 for x in s:
  st,en=get_span(x)
  if not (0<=st<en<=duration+.05):errors.append('Invalid scene span: '+str(x.get('id', x.get('name'))))
  if abs(st-cursor)>.05:errors.append(f'Scene gap/overlap at {st}')
  if not isinstance(x.get('kind'), str) or not x.get('kind'):errors.append('Missing or invalid scene kind: '+str(x.get('kind')))
  for n in x.get('nodes',[]):
   if not st<=n.get('at',st)<en:errors.append('Node outside scene')
  cursor=en
 if s and abs(cursor-duration)>.05:errors.append('Scenes must cover whole output duration')
 for o in p.get('overlays',[]):
  st,en=get_span(o)
  if not 0<=st<en<=duration+.05:errors.append('Invalid overlay span')
  for field in ['x','y','width','height']:
   if field not in o:errors.append('Overlay needs inspected-frame geometry: '+field)
  if all(f in o for f in ['x','y','width','height']):
   if o['x']<0 or o['y']<0 or o['width']<=0 or o['height']<=0 or o['x']+o['width']>m['width'] or o['y']+o['height']>m['height']:errors.append('Overlay outside canvas')
 if not (job/'transcript.json').exists():errors.append('Reviewed transcript.json missing')
 if not (job/'captions.json').exists():errors.append('Run captions after transcript review')
 if errors:raise ValueError('\n'.join(errors))
 return p,m
def cmd_validate(a):
 validate(Path(a.job));print('Plan bounds, coverage, overlay geometry and caption prerequisites passed; visual QA still required')
def cmd_timeline(a):
 job=Path(a.job);p,m=validate(job);fps=float(Fraction(m['fps']));caps=load(job/'captions.json');sc=p['scenes'];n=m['output_frame_count']
 def find(t):return next((s for s in sc if get_span(s)[0]<=t<get_span(s)[1]),sc[-1])
 with open(job/'frame-plan.csv','w') as o:
  w=csv.writer(o);w.writerow(['output_frame','seconds','scene','kind','active_overlays','caption'])
  for i in range(n):
   t=i/fps;s=find(t);w.writerow([i,t,s.get('id',s.get('name')),s['kind'],' | '.join(x.get('label',x.get('name','')) for x in p.get('overlays',[]) if get_span(x)[0]<=t<get_span(x)[1]),' '.join(x['text'] for x in caps if x['start']<=t<x['end'])])
 with open(job/'second-by-second.csv','w') as o:
  w=csv.writer(o);w.writerow(['start','end','scenes','graphics'])
  for t in range(math.ceil(m['duration'])):
   end=min(t+1,m['duration']);ss=[x for x in sc if get_span(x)[0]<end and get_span(x)[1]>t];w.writerow([t,end,' / '.join(x.get('title',x.get('name',x['kind'])) for x in ss),' / '.join(x.get('label',x.get('name','')) for x in p.get('overlays',[]) if get_span(x)[0]<end and get_span(x)[1]>t)])
 with open(job/'plan.md','w') as o:
  o.write('# Edit plan\n\n'+p.get('summary',p.get('through_line',''))+'\n\n| Seconds | Frames (end exclusive) | Visual | Content |\n|---|---|---|---|\n')
  for s in sc:
   st,en=get_span(s)
   o.write(f"| {st:.3f}–{en:.3f} | {round(st*fps)}–{round(en*fps)} | {s['kind']} | {s.get('title',s.get('name',''))} |\n")
 print('Plan Markdown, second and output-frame CSVs written; source PTS stay in analysis CSV')
def cmd_prepare(a):
 job=Path(a.job);m=manifest(job);vf=[]
 if m.get('colour_transfer') in ['arib-std-b67','smpte2084']:vf=['-vf','zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p']
 subprocess.run([binary('ffmpeg'),'-y','-v','warning','-threads','4','-i',m['source'],*vf,'-an','-c:v','libx264','-crf','16','-preset','fast','-threads','4','-pix_fmt','yuv420p','-r',m['fps'],'-frames:v',str(m['output_frame_count']),'-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',str(job/'working/source-rec709.mp4')],check=True)
 if m.get('has_audio',True):
  subprocess.run([binary('ffmpeg'),'-y','-v','error','-i',m['source'],'-vn','-ar','48000',str(job/'working/voice.wav')],check=True)
 else:
  subprocess.run([binary('ffmpeg'),'-y','-v','error','-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t',str(m['duration']),str(job/'working/voice.wav')],check=True)
def cmd_build(a):
 job=Path(a.job).resolve();p,m=validate(job);dest=job/'compositions/main';dest.mkdir(parents=True,exist_ok=True)
 for name in ['source-rec709.mp4','voice.wav']:
  source=job/'working'/name
  if not source.exists():raise ValueError('Run prepare first; missing '+name)
  (dest/'media').mkdir(exist_ok=True);shutil.copy2(source,dest/'media'/name)
 shutil.copytree(SKILL/'assets/icons',dest/'icons',dirs_exist_ok=True)
 shutil.copytree(job/'assets',dest/'assets',dirs_exist_ok=True)
 for svg in (dest/'icons').glob('*.svg'):
  data=svg.read_text().replace('currentColor','#408CFF')
  if svg.stem in ['nextdotjs','supabase','vercel','cloudflare','claude']:data=data.replace('<svg ','<svg fill="#408CFF" ')
  svg.write_text(data)
 shutil.copy2(SKILL/'assets/Poppins-Bold.ttf',dest/'Poppins-Bold.ttf')
 gsap=REPO/'node_modules/gsap/dist/gsap.min.js'
 if not gsap.exists():raise ValueError('Run npm ci at the editing repository root')
 shutil.copy2(gsap,dest/'gsap.min.js');style=load(SKILL/'assets/style.json')
 caps=[]
 for c in load(job/'captions.json'):
  for scene in p['scenes']:
   start=max(c['start'],scene['start']);end=min(c['end'],scene['end'])
   if start<end:caps.append({**c,'start':start,'end':end})
 config=dict(plan=p,style=style,captions=caps)
 text=(SKILL/'assets/hyperframes/index.html').read_text().replace('__CONFIG_JSON__',json.dumps(config,ensure_ascii=False).replace('<','\\u003c'))
 scale=m['width']/1080
 def css_scale(match):
  return '<style>'+re.sub(r'(?<![\w#.-])(\d+(?:\.\d+)?)px',lambda q:f'{float(q.group(1))*scale:g}px',match.group(1))+'</style>'
 text=re.sub(r'<style>(.*?)</style>',css_scale,text,flags=re.S)
 for key,value in dict(WIDTH=m['width'],HEIGHT=m['height'],DURATION=m['duration'],FPS=m['fps']).items():text=text.replace('__'+key+'__',str(value))
 (dest/'index.html').write_text(text);save(dest/'hyperframes.json',{'$schema':'https://hyperframes.heygen.com/schema/hyperframes.json','paths':{'blocks':'compositions','components':'compositions/components','assets':'assets'},'media':{'autoProxy':True}})
 print(dest)
def main():
 p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
 sub.add_parser('doctor').set_defaults(func=cmd_doctor)
 q=sub.add_parser('init');q.add_argument('source');q.add_argument('--out',dest='job',required=True);q.set_defaults(func=cmd_init)
 for command,func in [('analyze',cmd_analyze),('transcribe',cmd_transcribe),('captions',cmd_captions),('validate',cmd_validate),('timeline',cmd_timeline),('prepare',cmd_prepare),('build',cmd_build)]:
  q=sub.add_parser(command);q.add_argument('job');q.set_defaults(func=func)
  if command=='analyze':q.add_argument('--interval',type=float,default=1)
  if command=='transcribe':
   q.add_argument('--language',default='auto');q.add_argument('--model',default='small');q.add_argument('--device',default='cpu',choices=['cpu','cuda']);q.add_argument('--threads',type=int,default=4)
 a=p.parse_args()
 try:a.func(a)
 except (ValueError,RuntimeError) as e:p.exit(2,str(e)+'\n')
if __name__=='__main__':main()
