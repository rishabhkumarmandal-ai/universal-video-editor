#!/usr/bin/env node
import {spawnSync} from 'node:child_process';
import {existsSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname,resolve,delimiter} from 'node:path';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const local=[resolve(root,'.editing-tools/node_modules/ffmpeg-static'),resolve(root,'.editing-tools/node_modules/ffprobe-static/bin/linux/x64')].filter(existsSync);
const cli=resolve(root,'node_modules/hyperframes/bin/hyperframes.mjs');
if(!existsSync(cli)){process.stderr.write('Run npm ci in the editing repository first.\n');process.exit(2);}
const child=spawnSync(process.execPath,[cli,...process.argv.slice(2)],{stdio:'inherit',env:{...process.env,HYPERFRAMES_NO_TELEMETRY:'1',PATH:[...local,process.env.PATH||''].join(delimiter)}});
if(child.error){process.stderr.write(String(child.error)+'\n');process.exit(1);}process.exit(child.status??1);
