import console from 'node:console';
import process from 'node:process';
import { Buffer } from 'node:buffer';
import express from 'express';
import { createWriteStream } from 'fs';
import { mkdir } from 'fs/promises';
import path from 'path';
import { finished } from 'stream/promises';
import yazl from 'yazl';

import {
  buildUnityTemplate,
  sanitizeName,
  UNITY_VERSION,
  DEFAULT_PROJECT_NAME,
  DEFAULT_SCENE_NAME,
} from './template.js';

const { ZipFile } = yazl;

const app = express();
app.use(express.json({ limit: '1mb' }));

app.get('/healthz', (_req, res) => {
  res.json({
    ok: true,
    service: 'unity-exporter',
    unityVersion: UNITY_VERSION,
  });
});

app.post('/export', async (req, res) => {
  try {
    const projectName = sanitizeName(
      req.body?.projectName,
      DEFAULT_PROJECT_NAME
    );
    const sceneName = sanitizeName(req.body?.sceneName, DEFAULT_SCENE_NAME);

    const outDir = path.join(process.cwd(), 'downloads');
    await mkdir(outDir, { recursive: true });

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const zipFileName = `${projectName}-${timestamp}.zip`;
    const zipPath = path.join(outDir, zipFileName);

    const template = buildUnityTemplate({ projectName, sceneName });

    const zipFile = new ZipFile();
    const fileList = [];
    for (const [filePath, contents] of template.files.entries()) {
      zipFile.addBuffer(Buffer.from(contents, 'utf8'), filePath);
      fileList.push(filePath);
    }

    const outStream = createWriteStream(zipPath);
    zipFile.outputStream.on('error', (err) => outStream.destroy(err));
    zipFile.outputStream.pipe(outStream);
    zipFile.end();
    await finished(outStream);

    res.json({
      ok: true,
      path: zipPath,
      project: {
        name: projectName,
        scene: `${sceneName}.unity`,
        unityVersion: UNITY_VERSION,
        files: fileList,
      },
      instructions: template.instructions,
    });
  } catch (e) {
    res.status(500).json({ ok: false, error: String(e) });
  }
});

const port = process.env.PORT || 3000;
app.listen(port, () => console.log('unity exporter listening on', port));
