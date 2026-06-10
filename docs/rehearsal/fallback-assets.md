# Fallback assets (fill in during rehearsal)

Backups to switch to if the live run stalls (runbook §3). Keep the **raw video out of git**
(large binary) — store it in OneDrive/local and link it here. Commit the **screenshots**.

## Recording

- **Link:** _(OneDrive/local path to the screen recording of one clean 50/50 run)_
- **Captured:** _(date)_
- **Length / what it shows:** _(e.g. ~3 min: Reset → Step 1 → Step 2 → Step 3, MATLAB in sync)_
- [ ] Verified it plays back and is readable
- [ ] Open and ready to share during the call

## Screenshots

Saved in [screenshots/](screenshots/). Suggested set:

- [ ] `step1-figure.png` — MSD step response (displacement vs time)
- [ ] `step2-annotated.png` — overshoot + 2% settling marked
- [ ] `step3-simulink.png` — `mbd_demo.slx` overview + matching figure
- [ ] `error-card.png` — (optional) a staged error card, to show graceful failure
- [ ] `full-layout.png` — the 50/50 browser + MATLAB layout
