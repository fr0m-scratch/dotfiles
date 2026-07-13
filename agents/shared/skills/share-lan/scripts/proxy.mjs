import http from 'node:http';
import https from 'node:https';
import net from 'node:net';
import tls from 'node:tls';
import {createReadStream, existsSync, realpathSync, statSync} from 'node:fs';
import {extname, join, normalize, resolve, sep} from 'node:path';

const PORT = Number(process.env.PORT || 8088);
const HOST = '0.0.0.0';
const BACKEND = (process.env.BACKEND || '').replace(/\/$/, '');
const FRONTEND = process.env.FRONTEND || '.';
const API_PREFIXES = (process.env.API_PREFIXES || '/api').split(',').map((s) => s.trim()).filter(Boolean);
const FRONTEND_IS_URL = /^https?:\/\//.test(FRONTEND);
const MIME = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8', '.svg': 'image/svg+xml', '.png': 'image/png',
  '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.webp': 'image/webp',
  '.ico': 'image/x-icon', '.woff': 'font/woff', '.woff2': 'font/woff2', '.ttf': 'font/ttf',
  '.map': 'application/json', '.wasm': 'application/wasm', '.txt': 'text/plain; charset=utf-8',
};

const isApi = (url) => BACKEND && API_PREFIXES.some((p) => url === p || url.startsWith(`${p}/`) || url.startsWith(`${p}?`));

function proxyHttp(target, req, res) {
  const u = new URL(req.url, target);
  const secure = u.protocol === 'https:';
  const upstream = (secure ? https : http).request({
    method: req.method, hostname: u.hostname, port: u.port || (secure ? 443 : 80),
    path: u.pathname + u.search, headers: {...req.headers, host: u.host}, servername: u.hostname,
  }, (response) => {
    res.writeHead(response.statusCode || 502, response.headers);
    response.pipe(res);
  });
  upstream.on('error', (error) => {
    if (!res.headersSent) res.writeHead(502, {'content-type': 'text/plain; charset=utf-8'});
    res.end(`502 proxy: ${error.message}`);
  });
  req.pipe(upstream);
}

function serveStatic(directory, req, res) {
  const root = realpathSync(resolve(directory));
  const pathname = decodeURIComponent(new URL(req.url, 'http://local').pathname);
  let file = resolve(join(root, `.${pathname}`));
  if (file !== root && !file.startsWith(`${root}${sep}`)) {
    res.writeHead(403); res.end('403'); return;
  }
  if (existsSync(file) && statSync(file).isDirectory()) file = join(file, 'index.html');
  if (!existsSync(file)) file = join(root, 'index.html');
  if (!existsSync(file)) { res.writeHead(404); res.end('404'); return; }
  const actual = realpathSync(file);
  if (actual !== root && !actual.startsWith(`${root}${sep}`)) {
    res.writeHead(403); res.end('403'); return;
  }
  res.writeHead(200, {'content-type': MIME[extname(actual).toLowerCase()] || 'application/octet-stream'});
  createReadStream(actual).pipe(res);
}

const server = http.createServer((req, res) => {
  if (isApi(req.url)) return proxyHttp(BACKEND, req, res);
  if (FRONTEND_IS_URL) return proxyHttp(FRONTEND, req, res);
  return serveStatic(normalize(FRONTEND), req, res);
});

server.on('upgrade', (req, socket, head) => {
  const target = isApi(req.url) ? BACKEND : (FRONTEND_IS_URL ? FRONTEND : null);
  if (!target) return socket.destroy();
  const u = new URL(target);
  const secure = u.protocol === 'https:';
  const port = Number(u.port) || (secure ? 443 : 80);
  let upstream;
  const connected = () => {
    upstream.write(`${req.method} ${req.url} HTTP/1.1\r\n`);
    for (let i = 0; i < req.rawHeaders.length; i += 2) upstream.write(`${req.rawHeaders[i]}: ${req.rawHeaders[i + 1]}\r\n`);
    upstream.write('\r\n');
    if (head.length) upstream.write(head);
    socket.pipe(upstream); upstream.pipe(socket);
  };
  upstream = secure ? tls.connect(port, u.hostname, {servername: u.hostname}, connected) : net.connect(port, u.hostname, connected);
  upstream.on('error', () => socket.destroy());
  socket.on('error', () => upstream.destroy());
});

server.listen(PORT, HOST, () => {
  console.log(`[share] http://${HOST}:${PORT} frontend=${FRONTEND} backend=${BACKEND || '(none)'} api=${API_PREFIXES.join(',')}`);
});
