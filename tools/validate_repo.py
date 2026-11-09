#!/usr/bin/env python3
"""Check skill packaging and runnable helpers without rendering private media."""
from pathlib import Path
import ast,json,re,subprocess,sys
R=Path(__file__).resolve().parents[1];S=R/'skills/universal-video-editor'
text=(S/'SKILL.md').read_text();assert text.startswith('---\n') and 'name: universal-video-editor' in text and 'description:' in text
assert 'TODO' not in text
for target in re.findall(r'\]\(([^)]+)\)',text):
 if not target.startswith(('https:','http:')):assert (S/target).is_file(),target
for path in list((S/'scripts').glob('*.py'))+list((R/'tools').glob('*.py')):ast.parse(path.read_text(),filename=str(path))
style=json.load(open(S/'assets/style.json'));assert style['panels']['opacity']==style['panels']['iconTileOpacity']==1
assert style['palette']['blue']=='#408CFF' and style['palette']['blueText']=='#205AB0'
assert (S/'assets/Poppins-Bold.ttf').stat().st_size>50000
for name in ['clean-ui-reference.jpg','motion-collage-reference.jpg','approved-blue-edit.jpg']:assert (S/'assets/reference-style'/name).is_file()
subprocess.run(['node','--check',str(R/'tools/hyperframes.mjs')],check=True)
# Embedded generated browser JS must parse, without requiring runtime media.
html=(S/'assets/hyperframes/index.html').read_text();scripts=re.findall(r'<script>(.*?)</script>',html,re.S)
import tempfile
for script in scripts:
 with tempfile.NamedTemporaryFile(suffix='.js',mode='w') as f:
  f.write(script.replace('__CONFIG_JSON__','{}'));f.flush();subprocess.run(['node','--check',f.name],check=True)
print('Skill resources, helper syntax, deterministic template syntax and solid-background brand settings passed.')
