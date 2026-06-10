# Rehearsal & Teams-staging runbook (Slice 10)

The safety net for the live demo. Work through this **end-to-end at least once the day
before** and again **shortly before** the interview. It is deliberately manual (HITL): the
goal is a calm, repeatable run and a fallback if anything misbehaves live.

Demo target: a Microsoft Teams screen-share, browser + MATLAB R2026a side-by-side (50/50),
the chatbot driving MATLAB/Simulink live via MCP.

---

## 0. One-time / per-session setup

Run these **before every rehearsal and before the real call** (most must be redone after any
MATLAB or PC restart):

- [ ] **MATLAB R2026a open and visible** (not minimised — the audience watches it execute).
- [ ] **Share the session:** in the MATLAB Command Window run `shareMATLABSession`.
      ⚠️ NOT `matlab.engine.shareEngine`. Re-run after every MATLAB/PC restart.
- [ ] **Anthropic credentials present** (`ant auth login`, or `ANTHROPIC_API_KEY` in `.env`).
- [ ] **Clean MATLAB state:** `close all; clear; clc` so no stale figures/vars are on screen.
- [ ] **Launch via the pre-flight script:** `./run-demo.ps1` from the repo root. It fails loudly
      if MATLAB isn't shared/reachable — fix that *now*, not on the call. Wait for the browser
      to open at <http://127.0.0.1:8000>.
- [ ] **One throwaway warm-up run** (e.g. the **Extra-safe** button) so the first model call,
      engine attach, and figure export are already warm before anyone is watching.

---

## 1. Display tuning (the "narrow-column legibility" criterion)

Teams re-encodes the shared screen and the far end sees a compressed, often downscaled image.
Bias everything **larger and higher-contrast** than feels necessary locally.

**MATLAB Command Window + Editor font (~16–18 pt):**
- GUI (reliable, version-stable): **Home → Preferences → MATLAB → Fonts**. Set **Desktop code
  font** to **16–18 pt**. Under **Fonts → Custom**, bump the **Editor** and **Command Window**
  to the same if they don't inherit. Apply.
- Optional programmatic route (verify node names in your release first by inspecting `s = settings`):
  ```matlab
  s = settings;
  s.matlab.fonts.codefont.Size.PersonalValue = 18;   % desktop code font
  ```
- Make the **Command Window** the prominent MATLAB panel; close/shrink Workspace, Current
  Folder, and Editor panels you don't need on screen.

**Browser:**
- [ ] Zoom the demo UI to **110–125%** (Ctrl + `+`) so cards and code read at the far end.
- [ ] Full-screen the browser (F11) to drop tab/address-bar clutter.

**Window layout:**
- [ ] Snap **browser left ~50%, MATLAB right ~50%** (Win + ←/→).
- [ ] The timeline cards cap at **820 px**; on a 50/50 split of a 1080p screen (~960 px/half)
      they fit without horizontal clipping. Confirm code blocks wrap (they should) and figures
      render at column width. Confirm **click-to-lightbox** enlarges a figure full-screen.
- [ ] Windows display scaling: 100–125% is fine; avoid extremes that make MATLAB text tiny.

Record the values you settled on in [tuned-settings.md](tuned-settings.md).

---

## 2. The 3-run reliability protocol

Goal (PRD S1): **3 consecutive successful end-to-end runs, each starting from Reset, no crash.**
If a run fails, fix the cause and **restart the count from zero** — three *consecutive* clean runs.

**One run =** click **Reset** (`close all; clear`), then drive the scripted sequence and confirm
each beat:

| Beat | Action | Expect |
|------|--------|--------|
| Reset | **Reset** button | timeline clears to empty state; MATLAB figures close |
| Step 1 | **Step 1** | MATLAB MSD step response; a `check_matlab_code` beat; displacement-vs-time figure inline |
| Step 2 | **Step 2** | overshoot % + 2% settling time printed (computed from the array — no `stepinfo`); annotated figure |
| Step 3 | **Step 3** | `mbd_demo.slx` overview (read-only) → `sim` → logged signal read → figure matching Step 1 |
| (opt) Extra-safe | **Extra-safe** | sin/cos plot — the bulletproof fallback beat |

Watch for: figures appearing inline, the MATLAB window executing in sync, no error cards, the
model never being modified. Default model **Opus 4.8**; if a run is slow/flaky, the **Haiku 4.5**
selector is a faster fallback.

| Run | Date/time | Model | Reset | Step 1 | Step 2 | Step 3 | Result | Notes |
|-----|-----------|-------|-------|--------|--------|--------|--------|-------|
| 1   |           |       | ☐     | ☐      | ☐      | ☐      | PASS / FAIL | |
| 2   |           |       | ☐     | ☐      | ☐      | ☐      | PASS / FAIL | |
| 3   |           |       | ☐     | ☐      | ☐      | ☐      | PASS / FAIL | |

- [ ] **3 consecutive PASS achieved.**

---

## 3. Fallback assets (record one good run)

So a live failure is a shrug, not a disaster.

- [ ] **Screen-record one clean run** (Win + Alt + R, or OBS). Capture the 50/50 layout so the
      MATLAB-in-sync story is visible. Keep the raw video **out of git** (large binary) — store it
      in OneDrive/local and paste the **link** into [fallback-assets.md](fallback-assets.md).
- [ ] **Screenshots** of the key moments (Step 1 figure, Step 2 annotated figure, Step 3 Simulink
      overview + figure, an error card if you can stage one). Save PNGs into
      [screenshots/](screenshots/) and list them in [fallback-assets.md](fallback-assets.md).
- [ ] Have the recording **open and ready to share** during the call, so you can switch to it
      instantly if the live run stalls.

---

## 4. Teams 50/50 staging test

Do this on a **trial Teams call with a second person** (or a second device joined) to judge the
*far end* — you cannot assess compression from your own screen.

- [ ] Start a Teams call; **Share → Screen** (full screen, not just the browser window — the
      audience must see MATLAB executing too).
- [ ] On the **receiving** device, confirm at normal Teams window size:
  - [ ] Agent narration text is readable.
  - [ ] MATLAB code inside the tool cards is readable (syntax colors survive compression).
  - [ ] MATLAB Command Window output is readable.
  - [ ] Figures are legible inline; **click-to-lightbox** makes them clearly readable full-screen.
- [ ] If anything is marginal, return to **§1**, increase font/zoom, and re-test. Note final
      values in [tuned-settings.md](tuned-settings.md).

---

## 5. Go / No-go

- [ ] 3 consecutive clean runs (§2) ✔
- [ ] Fallback recording + screenshots saved and ready (§3) ✔
- [ ] Far-end legibility confirmed on a trial Teams call (§4) ✔
- [ ] Pre-flight (`run-demo.ps1`) green; `shareMATLABSession` muscle-memory rehearsed ✔

**Live-call ritual:** open MATLAB → `shareMATLABSession` → `./run-demo.ps1` (wait for green) →
warm-up Extra-safe run → Reset → share screen → begin. Recording open in the background.
