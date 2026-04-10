# Changelog

All notable changes to **FreeZap** are documented here. This project follows
[Keep a Changelog](https://keepachangelog.com/) and [Semantic Versioning](https://semver.org/).

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
