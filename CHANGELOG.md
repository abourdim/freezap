# Changelog

All notable changes to **FreeZap** are documented here. This project follows
[Keep a Changelog](https://keepachangelog.com/) and [Semantic Versioning](https://semver.org/).

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
