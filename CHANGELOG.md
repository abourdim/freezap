# Changelog

All notable changes to **FreeZap** are documented here. This project follows
[Keep a Changelog](https://keepachangelog.com/) and [Semantic Versioning](https://semver.org/).

## v1.1.2 — 2026-04-11

In-app FAQ refresh covering the v1.1 status pill and the experimental agent,
plus cleanup of four stale `v1.2` / `v1.1.0` version badges left over in the
header and sidebar footers after the v1.0.x / v1.1.x releases.

### Added
- **3 new FAQ entries** in the in-app Help panel, fully localized EN / FR / AR:
  - *"What's the colored pill at the top right?"* — documents all 6 states of
    the v1.0.3+ status pill (No code, Checking, Reachable, Unreachable, ✓ Ns
    ago, ✗ Ns ago) and the 20 s re-probe loop.
  - *"Can I see the current channel / volume / power state in FreeZap?"* —
    points at `freezap-agent/` for live enriched status.
  - *"Why is the FreeZap Agent marked experimental?"* — summarizes the 4
    failed Revolution pairing attempts and links to the known-limitation
    section in `freezap-agent/README.md` for workarounds (reusing an existing
    `app_token` from Home Assistant / Jeedom / freebox-api).
- 18 new i18n keys (`faq_q11..q13` + `faq_a11..a13` × 3 languages).

### Fixed
- 4 stale version badges in `index.html`:
  - main-card `.version-tag` showed `v1.2` (workshop-diy template leftover) → `v1.1.2`
  - Help panel `.sidebar-footer` badge `v1.2` → `v1.1.2`
  - Settings panel badge `v1.1.0` → `v1.1.2`
  - Log panel badge `v1.2` → `v1.1.2`

### Notes
- No JavaScript logic changes, no CSS changes, no agent changes. Pure
  documentation and version-label cleanup. 100% backward compatible.

## v1.1.1 — 2026-04-11

Docs-only patch marking the v1.1.0 agent pairing flow as **experimental /
unverified** after 4 real-world pairing attempts against a Freebox Revolution
(r1, `api_version: 15.0`) all timed out on the box side.

### Investigation summary

The HTTP protocol works:

- `POST /api/v6/login/authorize/` returns a valid `track_id` + `app_token` ✅
- `GET /api/v6/login/authorize/{track_id}` returns `status: "pending"` for ~50 s ✅
- After ~50 s the box transitions to `status: "timeout"` without ever accepting
  the physical validation (neither via the front-panel OLED nor via the
  Freebox OS web UI `Gestion des accès → Applications` tab)

The HMAC-SHA1 computation (`key=app_token`, `data=challenge`) and the session
login flow were not reached because pairing never completed. They remain
unit-tested in code but unverified against a live box.

### Changed

- **`freezap-agent/README.md`**: added a prominent `⚠️ Known limitation` section
  at the top documenting the 4 pairing attempts, the likely causes (Revolution
  OLED no longer rendering the prompt, firmware quirk, or authorization UI
  moved), and workarounds including **reusing an existing `app_token`** from
  Home Assistant / Jeedom / hacf-fr-freebox-api / Matschik-freebox by dropping
  it into `~/.freezap/token.json` as `{"app_token": "…"}`.
- **`README.md`**: the "Live player status" section now carries an explicit
  `⚠️ experimental` warning linking to the known limitation section.
- **No code change.** FreeZap continues to work exactly as in v1.1.0:
  - If the agent is absent / unpaired / unreachable → silent fallback to the
    v1.0.3 passive reachability pill
  - If the agent somehow succeeds in pairing (on Pop / Delta / Ultra, or on a
    Revolution with working UI) → rich pill with `📺 channel · 🔊 Vol N`

### Known issue tracked

If you own a working Freebox Revolution setup and can successfully pair the
agent, please open an issue or PR on the [FreeZap repo](https://github.com/abourdim/freezap)
describing how you triggered the validation prompt. That would help unblock
the feature for other Revolution owners.

## v1.1.0 — 2026-04-11

Real-time Freebox Player status via an optional local agent.

### Added — `freezap-agent/` (new directory)

- **`freezap-agent.py`** — ~400 lines of Python 3 stdlib only (no pip, no
  venv). A local HTTP bridge between FreeZap (browser JS) and the
  authenticated Freebox OS API (`mafreebox.freebox.fr/api/v6/...`). Handles:
  - **First-time pairing** via `POST /api/v6/login/authorize/`. Prints a
    banner and blocks until you press ✓ on the Freebox front-panel screen.
    Saves the `app_token` to `~/.freezap/token.json` with mode 0600.
  - **Per-session auth** via `GET /api/v6/login/` challenge → HMAC-SHA1
    (`key=app_token`, `data=challenge`) → `POST /api/v6/login/session/` →
    `X-Fbx-App-Auth` header. Session auto-renewed every 25 minutes.
  - **Player discovery** via `GET /api/v6/player/` (picks first Player).
  - **Background polling** every 2 seconds: `/api/v6/player/{id}/api/v7/status/`
    (power state + foreground app / channel) and `/api/v7/control/volume`
    (gracefully absent on some Revolution firmwares).
  - **CORS-enabled HTTP server** on `localhost:8766` exposing `/health`,
    `/status`, and a root index. OPTIONS preflight handled correctly.
- **`freezap-agent/start.sh`** — one-line launcher that checks for `python3`
  and runs the agent. Respects `FREEZAP_AGENT_PORT` env var.
- **`freezap-agent/README.md`** — full pairing walkthrough, endpoint docs,
  launchd (macOS) and systemd (Linux/Pi) service templates, security notes,
  and troubleshooting for the `/control/volume` unavailability on Revolution.

### Added — FreeZap (`script.js`, `index.html`)

- **Agent polling in `script.js`** — new constants (`FBX_AGENT_LS_KEY`,
  `FBX_AGENT_DEFAULT`, `FBX_AGENT_POLL_MS`, `FBX_AGENT_FRESH_MS`), new state
  (`fbxAgentData`, `fbxAgentTime`, `fbxAgentOk`, `fbxAgentPollId`), and four
  new functions: `fbxGetAgentUrl`, `fbxSetAgentUrl`, `fbxPollAgent`,
  `fbxStartAgentPolling` / `fbxStopAgentPolling`. Polls `/status` every 2 s.
- **Enriched `fbxRefreshStatus`** — new precedence cascade with agent data on
  top, falling back cleanly to the v1.0.3 reachability pill when the agent is
  absent, unreachable, or returns stale data (> 6 s old).
- **Six new pill states** driven by agent data:
  - 🟢 `📺 <channel>` — powered + current TV channel
  - 🟢 `🟢 On` / `Allumée` / `مُشغَّلة` — powered, not on TV
  - 🟡 `😴 Standby` / `En veille` / `في وضع السكون` — Player in standby
  - 🔴 `✗ Agent error` — agent running but Freebox API failed
  - 🟢 Any of the above + `🔊 Vol {n}` when volume endpoint is exposed
  - 🔇 `Vol {n}` with mute icon when muted
- **New Settings field** in `index.html`: `#rcAgentUrl` text input for the
  agent URL, with i18n label and helper hint pointing at the README.
  Value persisted in `localStorage['fbx_agent_url']`, defaults to
  `http://localhost:8766`.
- **11 new i18n keys** per language (EN / FR / AR): `statusStandby`,
  `statusPowered`, `statusVol`, `statusAgentError`, `agentUrlLabel`,
  `agentUrlHint`, `agentUrlPlaceholder`.

### Design notes

- **Backward compatible**: an empty agent URL or unreachable agent degrades
  silently to the v1.0.3 behaviour. No breakage for existing users.
- **Fully optional**: the agent lives in its own subdirectory and has its own
  README. FreeZap's single-file static deployment still works without it.
- **Single Python process**: no threads beyond the polling worker + HTTP
  server's threading mixin. No external dependencies, no virtualenv, no pip.
- **Mixed-content bonus**: in a future v1.2 we can route remote key presses
  through the agent as well (`POST /key/<name>`), which would remove the
  `chrome://settings/content/insecureContent` requirement for GitHub Pages
  users on mobile. Not wired in v1.1.0 — keys still go to `hd1.freebox.fr`
  via the legacy unauthenticated endpoint.

### Security

- The `app_token` is a long-lived credential. The agent saves it to
  `~/.freezap/token.json` with file mode `0600`. Revocable from Freebox OS
  under *Paramètres de la Freebox → Gestion des accès → Applications*.

## v1.0.3 — 2026-04-10

Freebox reachability status in the header pill.

### Added
- **Live status pill** (top-right of the header) now shows one of:
  - 🟡 *No code* — no remote code saved yet, no probing.
  - ⚪ *Checking…* — initial LAN probe in flight (< 3 s).
  - 🟢 *Freebox reachable* — probe succeeded (`http://hd1.freebox.fr/` responded).
  - 🔴 *Freebox unreachable* — probe rejected (DNS / timeout / network).
  - 🟢 *✓ {n}s ago* — last key press succeeded (fresh within 8 s).
  - 🔴 *✗ {n}s ago* — last key press threw a network error.
- **Silent reachability probe** on page load + every 20 s heartbeat while a
  code is set. Probes hit the Freebox Server root URL (not `/pub/remote_control`),
  so no actual key is sent during probes.
- **Per-TX tracking**: `fbxSendKey` flips the pill immediately after each
  tap based on whether `fetch()` resolved or rejected.
- 5 new i18n keys (`statusNoCode`, `statusChecking`, `statusReachable`,
  `statusUnreachable`, `statusLastTx`) fully localized EN / FR / AR.

### Known limits (documented honestly in the FAQ)
- The pill reflects **LAN reachability of the Freebox Server**, not the
  specific state of the Player (the `hd1.freebox.fr` URL is served by the
  Server, not the Player directly).
- The pill **cannot** tell you whether your remote code is correct — the
  no-cors opaque response hides the HTTP status code. A 🟢 pill just means
  "the network path to the box is up and the last fetch didn't throw".

## v1.0.2 — 2026-04-10

FAQ expansion — all the useful answers now live in the in-app Help panel,
fully translated across EN / FR / AR.

### Added
- **6 new FAQ entries** in the Help panel (tap ❓ in the header):
  - *FreeZap loads but no buttons work (GitHub Pages / HTTPS). How do I unblock it?*
    → step-by-step for `chrome://settings/content/insecureContent` + caveat
    that it does not work on Safari iOS / Chrome Android.
  - *How do I use FreeZap on my phone?* → `./serve.sh` local HTTP server.
  - *Does FreeZap work with my Freebox Pop / Delta / Ultra?* → No, Revolution only.
  - *Can I control FreeZap with the keyboard?* → full shortcut list.
  - *Does FreeZap need an internet connection?* → No, LAN only.
  - *What is "long press"?* → 500 ms hold sends `&long=true`.
- All new FAQ strings localized in English, French, Arabic.

## v1.0.1 — 2026-04-10

Tested live on a Freebox Revolution (v6) Player. Bug fixes and mobile polish.

### Fixed
- **Wrong menu path in doc**: the README and in-app setup steps pointed to
  *Freebox OS → Personnaliser la télécommande* (which is actually the
  key-remapping menu, not the network remote code). Corrected in both the
  README and the i18n `setup_1..setup_4` / `faq_a2` strings across EN / FR / AR.
  The real path is *Freebox Player TV → Free → Réglages → Système →
  Informations Freebox Player et Server → « Code télécommande réseau »*.
- Visual press-state now lingers 80 ms after pointer release so iOS users
  (where `navigator.vibrate` is a no-op) still get a clear tap confirmation.

### Added
- **`serve.sh`** — one-line helper that prints the Mac's LAN IP and launches
  `python3 -m http.server` so phones on the same Wi-Fi can reach FreeZap
  over plain HTTP (bypasses the mixed-content trap entirely).
- Mobile CSS polish:
  - `viewport-fit=cover` + `env(safe-area-inset-*)` body padding for iPhone
    notch / home bar safety.
  - `touch-action: manipulation` on all tappable elements — kills the 300 ms
    tap delay and accidental double-tap-to-zoom.
  - `overscroll-behavior: none` on `<html>`/`<body>` — no more rubber-band
    bounce when scrolling the keypad on iOS.
  - `-webkit-text-size-adjust: 100%` to prevent iOS landscape text inflation.
  - Code input font-size pinned to 16 px to avoid iOS focus-zoom.
  - `< 560 px` media query: hides bismillah, workshop-diy logo, subtitle,
    footer, and status pill to give the keypad maximum vertical real estate.
  - `< 380 px` media query: shrinks title and keypad gaps for very small phones.
- README: new **Mixed-content warning** table, **Option 2 (serve.sh)** quick
  start for phones, and explicit "Pages doesn't work on mobile" caveat in
  **Option 3**.

## v1.0.0 — 2026-04-10

Initial release.

### Added
- Full Freebox Player keypad: power, sources (TV / list / EPG / media), info row,
  D-pad with OK, side controls (vol ± / ch ±), numeric pad, color buttons,
  media transport (prev / bwd / play / fwd / next / rec).
- Long-press detection: holding any button for 500 ms sends the key with
  `&long=true` (matches the official Freebox HTTP remote API).
- Keyboard shortcuts: arrows / Enter / Esc / Space / + / − / m / h / 0–9.
- Trilingual UI (English / Français / العربية with RTL), defaults to French.
- 8 visual themes (Mosque, Zellige, Andalous, Riad, Médina, Space, Jungle, Robot)
  inherited from the workshop-diy template.
- Activity log: every key press is recorded as a TX entry; errors as ✗.
- Haptic feedback on mobile (`navigator.vibrate`).
- Remote code persisted in `localStorage`.
- PWA installable with a single SVG icon (favicon + maskable).
