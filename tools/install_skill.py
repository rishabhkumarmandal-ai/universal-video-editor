#!/usr/bin/env python3
"""Link this repository's skill into local Codex discovery without overwriting other skills."""
from pathlib import Path
import os
repo=Path(__file__).resolve().parents[1];source=repo/'skills/universal-video-editor'
base=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'skills';base.mkdir(parents=True,exist_ok=True);target=base/source.name
if target.is_symlink() and target.resolve()==source:print('Already installed:',target)
elif target.exists() or target.is_symlink():raise SystemExit(f'Refusing to replace existing skill: {target}')
else:target.symlink_to(source,target_is_directory=True);print('Installed:',target,'→',source)
