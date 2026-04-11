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
| **Freebox Revolution (v6) Player** | ✅ Works — uses the legacy unauthenticated `hd1.freebox.fr/pub/remote_control` API. **Tested v1.0.1.** Live status available via the optional [FreeZap Agent](./freezap-agent/) (v1.1.0+). |
| **Freebox Pop / Delta / Ultra (v7+)** | ❌ Not supported — these boxes use a different, authenticated API. FreeZap will not control them. |
| Freebox without a TV Player | ❌ Nothing to control. |

---

## 📡 Live player status (optional, v1.1.0+)

Out of the box FreeZap only knows *"the Freebox responds on the LAN"*. If you
want the header pill to show **real-time player state** (powered / in standby,
current channel, volume, mute), install and run the **[FreeZap Agent](./freezap-agent/)**
— a ~400-line Python 3 stdlib script that lives in `freezap-agent/` and acts
as a local authenticated bridge to the Freebox OS API.

Enhanced pill states (when the agent is running):

- 🟢 **`📺 TF1 · 🔊 Vol 42`** — Player running, on channel TF1, volume 42
- 🟡 **`😴 En veille`** — Player in standby
- 🔴 **`✗ Agent KO`** — agent running but can't reach the Freebox

```bash
cd freezap-agent
./start.sh
# → asks you to press ✓ on the Freebox front panel (one-time pairing)
# → runs on http://localhost:8766/ with /health and /status endpoints
```

Then in FreeZap open **Settings (⚙️)** and paste `http://localhost:8766` into
the **FreeZap Agent URL** field (or leave the default, it's already pointed
there). FreeZap polls `/status` every 2 seconds and upgrades the pill.

**The agent is optional.** If you don't run it, or if its URL is unreachable,
FreeZap silently falls back to the v1.0.3 passive reachability pill
(`Joignable` / `Injoignable` / `Last TX: Ns ago`). No breakage.

See [freezap-agent/README.md](./freezap-agent/README.md) for pairing details,
security notes, launchd/systemd service templates, and troubleshooting.

---

## ⚠️ Mixed-content warning — read this before hosting

FreeZap calls `http://hd1.freebox.fr` over plain HTTP. If you load FreeZap
itself over `https://`, browsers enforce their mixed-content policy:

| Host | Desktop Chrome / Firefox | Safari iOS | Chrome Android |
|---|---|---|---|
| `file://` (local file) | ✅ works | — | — |
| `http://192.168.x.x:PORT` (LAN HTTP server) | ✅ works | ✅ works | ✅ works |
| `https://*.github.io/...` (GitHub Pages) | ⚠️ blocked by default, but **can be whitelisted per-site** in desktop Chrome only | ❌ **impossible to unblock** | ❌ **option removed from UI** |
| Any other HTTPS host (Netlify, Vercel…) | ⚠️ same as above | ❌ same | ❌ same |

**Bottom line:** if you want FreeZap to work on your phone, **do not rely
on GitHub Pages**. Serve it over plain HTTP from your LAN (see below).

---

## 🚀 Quick start

### Option 1 — local file on your laptop (simplest)
```bash
git clone https://github.com/abourdim/freezap.git
cd freezap
open index.html           # macOS
xdg-open index.html       # Linux
start index.html          # Windows
```
Works immediately. No phone support — laptop only.

### Option 2 — serve from your Mac on your LAN (works on phones)
```bash
cd freezap
./serve.sh                # defaults to port 8000
# or: ./serve.sh 9000 to pick another port
```
The script prints the exact URL to open on your phone, e.g.
`http://192.168.1.15:8000/`. On your phone (same Wi-Fi), open that URL in
Safari or Chrome and use **Add to Home Screen** to install FreeZap as a PWA.

Keep the Mac terminal running as long as you want the remote to be reachable.
For a permanent setup, run `serve.sh` on a Raspberry Pi, a NAS, or any
always-on machine on your LAN.

### Option 3 — GitHub Pages (desktop Chrome only, requires manual unblock)
1. Open `https://abourdim.github.io/freezap/` in desktop Chrome.
2. Go to `chrome://settings/content/insecureContent`.
3. Under *Allowed to show insecure content* click **Add** and enter
   `https://abourdim.github.io`.
4. Reload the FreeZap tab. It will now work, with a permanent
   *Not Secure* warning in the omnibox (expected).

⚠️ This trick **does not work on phones** (Safari iOS forbids mixed content
outright, Chrome Android hides the toggle). Use Option 2 for phones.

---

## 🔑 First-time setup — find your remote code

The remote code lives on the **Freebox Player** (the TV box), not on
`mafreebox.freebox.fr` (the router). You need to read it from the TV using
your physical Freebox remote.

1. Turn on the TV on the Freebox channel.
2. Press the **Free** button (🏠 home) on the physical remote.
3. Go to **Réglages** (⚙️) → **Système** → **Informations Freebox Player et Server**.
4. Find the line **« Code télécommande réseau »** — it's an 8-digit code
   auto-generated by the Player.
5. Open FreeZap, paste the 8 digits into the **Code** field, press **Enregistrer**.
6. The code is stored in your browser's `localStorage` and never leaves
   the device.

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

**Long press** any on-screen button (≥ 500 ms) to send the key with the
`long=true` flag — matches the behaviour of holding the physical remote.

---

## ✨ Features

- 📺 Full keypad: power, TV/list/EPG/media, D-pad, OK, vol ±, channel ±, 0–9, color buttons, media transport (prev/bwd/play/fwd/next/rec)
- 🌍 Trilingual UI: 🇫🇷 FR (default) · 🇬🇧 EN · 🇩🇿 AR (with RTL layout)
- 🎨 8 visual themes (Mosque, Zellige, Andalous, Riad, Médina, Space, Jungle, Robot)
- ⌨️ Keyboard shortcuts (see above)
- 📳 Haptic feedback on Android (`navigator.vibrate`) + visual press flash fallback for iOS
- 📜 Activity log with TX/error tracing
- 💾 Remote code persisted in `localStorage`
- 📱 PWA installable, works offline once cached, iPhone notch-safe (`env(safe-area-inset-*)`)
- 🔒 Local-first: no analytics, no telemetry, no third-party calls

---

## 📁 Project structure

| File | Purpose |
|---|---|
| `index.html` | UI: keypad, header, panels, all markup, mobile CSS |
| `script.js` | i18n, themes, panels, log, Freebox remote logic (`fbxSendKey`, long-press, keyboard) |
| `style.css` | 8-theme system, responsive layout, animations (inherited from workshop-diy template) |
| `manifest.json` | PWA manifest |
| `icon.svg` | Single vector icon (favicon + PWA install + maskable) |
| `serve.sh` | One-line local HTTP server helper, prints your LAN URL for the phone |

No build step, no dependencies, no `node_modules`. Just open `index.html`
or run `./serve.sh`.

---

## 🔒 Privacy

- The remote code lives **only** in your browser's `localStorage`.
- Every key press is a single direct GET to `http://hd1.freebox.fr` on your
  LAN — nothing transits any third-party server.
- No analytics, no telemetry. The only external request at load time is
  the Google Fonts CSS import in `<head>` — you can remove that line if
  you want zero external requests.

---

## 🙏 Credits

FreeZap is built on top of the **[Workshop-DIY web app template](https://github.com/abourdim)**
by abourdim — themes, i18n, panels, log system, splash, and PWA shell are
inherited from that template. The Freebox remote keypad and key dispatch
logic are added on top.

The Freebox HTTP remote control API is documented in many community
projects; the endpoint `http://hd1.freebox.fr/pub/remote_control?code=XXXXXXXX&key=KEY`
has been stable since the Freebox Revolution Player.

---

## 📄 License

MIT — see [LICENSE](./LICENSE).
