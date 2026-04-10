# 📺 FreeZap

> A web-based remote for the Freebox Player. Pilot your box from any phone,
> tablet, or laptop on the same Wi-Fi — no app store, no install, no account.

FreeZap is a single-page web app that talks to the official Freebox HTTP
remote control endpoint (`http://hd1.freebox.fr/pub/remote_control`). Tap
buttons, get the same effect as your physical remote. Supports trilingual
UI (FR / EN / AR), 8 visual themes, keyboard shortcuts, long-press, and
PWA install.

---

## ⚠️ Compatibility

| Freebox model | Status |
|---|---|
| **Freebox Revolution (v6) Player** | ✅ Works — uses the legacy unauthenticated `hd1.freebox.fr/pub/remote_control` API. |
| **Freebox Pop / Delta / Ultra (v7+)** | ❌ Not supported — these boxes use a different, authenticated API. FreeZap will not control them. |
| Freebox without a TV Player | ❌ Nothing to control. |

To check: if you can open `http://hd1.freebox.fr/pub/remote_control?code=XXXXXXXX&key=ok`
in a browser on your LAN and your TV reacts, you're good.

---

## ⚠️ Mixed-content warning — read this before hosting

FreeZap **must be served over `http://` or opened directly from disk
(`file://`)**. It calls `http://hd1.freebox.fr` over plain HTTP — if the page
itself is loaded over `https://`, modern browsers will silently block those
calls as mixed content and nothing will happen.

This means you **cannot** host FreeZap on:
- GitHub Pages
- Netlify
- Cloudflare Pages
- any HTTPS-only host

You **can** run it from:
- a local file (`file:///…/index.html`)
- a tiny local HTTP server on the same LAN as the Freebox
- a self-hosted box / Raspberry Pi serving over plain HTTP on your LAN

---

## 🚀 Quick start

### Option 1 — open directly from disk
```bash
open index.html              # macOS
xdg-open index.html          # Linux
start index.html             # Windows
```

### Option 2 — serve over local HTTP (best for "Add to Home Screen")
```bash
cd freezap
python3 -m http.server 8000
# then open http://<your-mac-lan-ip>:8000/ on your phone
```

### Option 3 — install as a PWA on your phone
1. Serve over local HTTP (Option 2).
2. Open the page in Safari (iOS) or Chrome (Android) on the same Wi-Fi.
3. Use *Add to Home Screen*. The icon installs and FreeZap opens fullscreen.

---

## 🔑 First-time setup

1. Open Freebox OS (`http://mafreebox.freebox.fr`) on the same network.
2. Go to **Paramètres de la Freebox → Personnaliser la télécommande**.
3. Set or read your 8-character remote code.
4. Open FreeZap, paste the code in the field at the top, click **Enregistrer**.
   The code is stored in your browser's `localStorage` and never leaves the device.

---

## ⌨️ Keyboard shortcuts

| Key | Action |
|---|---|
| `← → ↑ ↓` | Navigate |
| `Enter` | OK |
| `Esc` / `Backspace` | Back |
| `Space` | Play / Pause |
| `+` / `-` | Volume up / down |
| `m` | Mute |
| `h` | Home |
| `i` | Info |
| `0` – `9` | Digits |

**Long press** any on-screen button (≥ 500 ms) to send the key with the `long=true` flag — matches the behaviour of holding the physical remote.

---

## ✨ Features

- 📺 Full keypad: power, TV/list/EPG/media, D-pad, OK, vol ±, channel ±, 0–9, color buttons, media transport (prev/bwd/play/fwd/next/rec)
- 🌍 Trilingual UI: 🇫🇷 FR (default) · 🇬🇧 EN · 🇩🇿 AR (with RTL layout)
- 🎨 8 visual themes (Mosque, Zellige, Andalous, Riad, Médina, Space, Jungle, Robot)
- ⌨️ Keyboard shortcuts (see above)
- 📳 Haptic feedback on mobile
- 📜 Activity log with TX/error tracing
- 💾 Remote code persisted in `localStorage`
- 📱 PWA installable, works offline once cached
- 🔒 Local-first: no analytics, no telemetry, no third-party calls

---

## 📁 Project structure

| File | Purpose |
|---|---|
| `index.html` | UI: keypad, header, panels, all markup |
| `script.js` | i18n, themes, panels, log, Freebox remote logic (`fbxSendKey`, long-press, keyboard) |
| `style.css` | 8-theme system, responsive layout, animations |
| `manifest.json` | PWA manifest |
| `icon.svg` | Single vector icon (favicon + PWA install + maskable) |

No build step, no dependencies, no node_modules. Just open `index.html`.

---

## 🔒 Privacy

- The remote code lives **only** in your browser's `localStorage`.
- Every key press is a single direct GET to `http://hd1.freebox.fr` on your
  LAN — nothing transits any third-party server.
- No analytics, no telemetry, no fonts loaded over the network at runtime
  except the Google Fonts CSS in `<head>` (you can remove that line if you
  want zero external requests).

---

## 🙏 Credits

FreeZap is built on top of the **[Workshop-DIY web app template](https://github.com/abourdim)**
by abourdim — themes, i18n, panels, log system, splash, and PWA shell are
inherited from that template. The Freebox remote keypad and key dispatch
logic are added on top.

The Freebox HTTP remote control API is documented in many community projects;
the endpoint `http://hd1.freebox.fr/pub/remote_control?code=XXXXXXXX&key=KEY`
has been stable since the Freebox Revolution Player.

---

## 📄 License

MIT — see [LICENSE](./LICENSE).
