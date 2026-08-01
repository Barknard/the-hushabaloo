/**
 * Assemble the site the way the Pages workflow does, then serve it from the same
 * subpath Pages serves it from: http://127.0.0.1:4173/the-hushabaloo/
 *
 *   node tools/serve-site.mjs
 *
 * The subpath is the whole point. Serving from the root would let an absolute
 * "/audio/x.mp3" resolve fine locally and 404 for every real visitor.
 */
import { createServer } from 'node:http';
import { readFile, mkdir, cp, rm, access } from 'node:fs/promises';
import { join, extname, resolve, normalize } from 'node:path';

const ROOT = resolve(import.meta.dirname, '..');
const SITE = join(ROOT, '.site');
const PREFIX = '/the-hushabaloo/';
const PORT = 4173;

const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.mp3': 'audio/mpeg',
  '.svg': 'image/svg+xml',
};

async function assemble() {
  await rm(SITE, { recursive: true, force: true });
  await mkdir(SITE, { recursive: true });
  await cp(join(ROOT, 'player', 'index.html'), join(SITE, 'index.html'));
  await cp(join(ROOT, 'audio'), join(SITE, 'audio'), { recursive: true });
  await rm(join(SITE, 'audio', 'provenance.json'), { force: true });
}

await assemble();

createServer(async (req, res) => {
  let path = decodeURIComponent(new URL(req.url, 'http://x').pathname);

  if (!path.startsWith(PREFIX)) {
    res.writeHead(404).end('Not found — the site lives at ' + PREFIX);
    return;
  }
  path = path.slice(PREFIX.length) || 'index.html';
  if (path.endsWith('/')) path += 'index.html';

  // Keep traversal inside the served directory.
  const file = join(SITE, normalize(path).replace(/^(\.\.[/\\])+/, ''));
  if (!file.startsWith(SITE)) {
    res.writeHead(403).end('Forbidden');
    return;
  }

  try {
    await access(file);
    const body = await readFile(file);
    res.writeHead(200, {
      'Content-Type': TYPES[extname(file)] ?? 'application/octet-stream',
      'Content-Length': body.length,
      'Cache-Control': 'no-store',
    });
    // HEAD is used by the suite to check every audio URL resolves.
    res.end(req.method === 'HEAD' ? undefined : body);
  } catch {
    res.writeHead(404).end('Not found: ' + path);
  }
}).listen(PORT, '127.0.0.1', () => {
  console.log(`serving ${SITE}\n  -> http://127.0.0.1:${PORT}${PREFIX}`);
});
