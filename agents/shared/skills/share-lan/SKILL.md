---
name: share-lan
description: Expose a local frontend and its backend to devices on the same Wi-Fi through one verified same-origin reverse proxy. Use when the user asks to share, demo, or open a local web app on a phone, tablet, or another LAN device.
---

# Share on LAN

Only perform this workflow when the user explicitly asks to expose an app on the local network.

1. Determine the LAN IP from `ipconfig getifaddr en0`, falling back to `en1`. Stop if neither exists.
2. Select the requested public port or the first free port from 8088 upward.
3. Identify the frontend as either a localhost dev-server URL or an absolute static directory. Start it on `127.0.0.1`, not `0.0.0.0`.
4. Identify the backend URL and actual API path prefixes from code/config. Start the backend on localhost when needed. Do not invent a backend.
5. Start the bundled zero-dependency proxy; it is the only process that binds all interfaces:

   ```bash
   SKILL_DIR="${SHARE_LAN_SKILL_DIR:-$HOME/.agents/skills/share-lan}"
   PORT=<port> FRONTEND=<dir-or-url> BACKEND=<url-or-empty> API_PREFIXES=/api \
     node "$SKILL_DIR/scripts/proxy.mjs"
   ```

6. Verification is mandatory. Curl `http://<LAN_IP>:<PORT>/` and require 2xx/3xx. If a backend exists, curl a real backend route through the LAN proxy and require a backend response, not the proxy's 502.
7. Report the LAN URL, observed frontend/backend status codes, and process IDs. Print a QR code only when `qrencode` is already installed.

Never tell a phone to use localhost. Never claim sharing is complete before the LAN-address checks pass. Do not weaken firewalls or expose the backend directly.
