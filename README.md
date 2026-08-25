# Professor OS — Robotics Teacher Agent (Python 3.7)

**Built by Connect.Vin**


A sequential autonomous robotics teacher for Python 3.7. It generates one curriculum-linked class at a time, validates the lesson and runnable Python examples, creates local lesson artifacts, optionally publishes them to GitHub and LinkedIn, and exposes the entire backend workflow on a live single-page local dashboard.

## What changed in this hardened build

- Added retry + exponential backoff for OpenAI/network/DNS failures.
- Added human-readable error messages for API failures.
- Fixed the validator environment bug: generated code now inherits the current process environment instead of losing it.
- Added separate preview and published course memory. Preview runs can advance without falsely claiming that classes were published.
- Added v1 progress-file migration.
- Each Python code block is saved as its own validated `code/lab_XX.py` file instead of concatenating unrelated programs and calling the result verified.
- Added a lesson-specific concept-map image instead of reusing exactly the same diagram for every class.
- Hardened GitHub configuration checks and API requests.
- LinkedIn publishing POSTs are intentionally not blindly retried, preventing accidental duplicate public posts after an ambiguous connection failure.
- Added a per-run lock so two classes cannot execute concurrently.
- Added persistent runtime state and `teacher_agent.log`.
- Added a built-in Python 3.7 HTTP dashboard with no Flask dependency.
- Added a built-in 4:30 PM IST scheduler with no APScheduler dependency.
- Added `pytest.ini` so `teacher_agent` imports correctly when running tests from the project root.
- Expanded tests for retry behavior, progress/migration, validator, and dashboard state.

## Dashboard: Professor OS

The dashboard is not a mock animation. It reads the actual runtime state emitted by the pipeline.

It shows:

- current class and curriculum position;
- current backend operation;
- lesson generation state;
- network retries;
- validation and repair activity;
- visual generation;
- new files/code artifacts;
- GitHub and LinkedIn stages;
- persistent event stream;
- last error;
- preview/publish course memory;
- next scheduled 4:30 PM IST run;
- a **Run Class Now** control.

## Python 3.7 installation

From the project root:

```bash
python3.7 -m venv .linkvenv
source .linkvenv/bin/activate
python -m pip install --upgrade "pip<24.1"
python -m pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and at minimum set:

```env
OPENAI_API_KEY=YOUR_KEY
OPENAI_MODEL=gpt-5
AUTO_PUBLISH=false
```

## Verify before running

```bash
python -m pytest -v
```

## Start the OS-style dashboard

```bash
python -m teacher_agent.main --dashboard
```

Then open:

```text
http://127.0.0.1:8765
```

By default the dashboard also activates the daily **4:30 PM IST** scheduler.

To run the dashboard without its scheduler:

```env
DASHBOARD_SCHEDULE=false
```

## Generate one class from the terminal

```bash
python -m teacher_agent.main --once
```

With `AUTO_PUBLISH=false`, artifacts appear under:

```text
preview/
  001-what-is-a-robot/
    README.md
    diagram.png
    code/
      lab_01.py
      lab_02.py
```

## Scheduler without dashboard

```bash
python -m teacher_agent.main --scheduler
```

This process must remain running. It triggers at 16:30 IST every day.

## Publishing

Keep this during development:

```env
AUTO_PUBLISH=false
```

Only set:

```env
AUTO_PUBLISH=true
```

after OpenAI, GitHub and LinkedIn credentials have been configured and several preview classes have been reviewed.

## Runtime files

The agent writes:

```text
.robotics_teacher_progress.json
.robotics_teacher_runtime.json
teacher_agent.log
```

`progress` is the course memory. `runtime` is the live dashboard state. `teacher_agent.log` is the durable event history.

## Network retry settings

```env
OPENAI_TIMEOUT=180
API_MAX_ATTEMPTS=5
API_RETRY_BASE_DELAY=2
```

The retry sequence uses exponential backoff with small jitter. DNS/temporary connection failures no longer immediately kill OpenAI generation or repair requests.

## Production note

Python 3.7 is end-of-life. This build is intentionally compatible with it because the target machine requires it. For a new deployment, migrate to a currently supported Python version when practical.

## UI Theme

The local dashboard uses a turquoise-blue operating-system aesthetic with a live lecture navigator and only working controls.


## Dashboard Polish

The dashboard includes senior-level UI refinements and visible integration indicators for GitHub and LinkedIn configuration state.


## Teacher Live Core

The dashboard now includes a 3D floating responsive Teacher Live Core inspired by a voice-assistant orb, with the status text changing to `Teaching...` while the agent is actively running.


## UI and Sync Fixes

- The dashboard now detects when a generated lecture folder has been deleted locally.
- Such lectures are marked as `missing` instead of incorrectly showing `generated`.
- The next preview run regenerates the earliest missing lecture automatically.
- Generated counts in the UI now reflect real available preview packages, not just stored progress.
- Added live data-health indicators to highlight sync issues.


## Automatic validated source sync

When `AUTO_SYNC_SOURCE=true`, Professor OS watches its application source. A changed source snapshot is pushed to the configured GitHub repository only after `pytest -q` and Python compile checks both pass. `.env`, tokens, logs, local runtime state, virtual environments, caches, and preview content are excluded from source sync.

## v10.1 Editorial JSON Reliability Fix

Premium editorial reviews now use OpenAI Responses API Structured Outputs with a strict JSON schema. The runtime also includes conservative local JSON repair, two automatic structured repair attempts, and a blocking fallback review. A malformed reviewer response can no longer terminate Professor OS with a JSONDecodeError; if repair ultimately fails, publication is safely blocked and the reason is surfaced in the dashboard/log instead.


## v10.2 — Post-media remediation

The final editorial review now runs after the Professor OS hero and engineering schematic are rendered and the schematic is inserted into the lesson. A weak post-media dimension such as `visual_teaching_plan=74` triggers targeted remediation and re-review instead of immediately killing the run. `POST_MEDIA_REPAIR_ROUNDS=2` controls the retry budget. Source-code sync errors are also isolated from teaching-run health and no longer mark the GitHub integration itself as disconnected.


## v10.3 — Automatic technical correction

Blocking factual, mathematical, simulation, code-semantic, and internal-consistency findings are no longer treated as immediate runtime failures. Professor OS now sends the exact blocking review back through a dedicated senior-faculty technical-correction pass, reruns the full lesson/code validator, and asks the editorial board to verify the corrected result. `TECHNICAL_QUALITY_REPAIR_ROUNDS=3` controls this repair budget.

For example, a contradiction between a sensor-bias derivation and the simulated plant, or a boundary-classification bug in generated Python, is corrected in both prose and code before the article can continue to LinkedIn preflight. If all repair attempts are exhausted, the run enters a safe **Publication Hold** state instead of reporting an agent-startup crash. The class is not marked complete or published, and it can be rerun after correction.


## v11.0 — Gemini Premium Visual Website

This version upgrades Professor OS from a dashboard-first tool into a **student-facing website** with a nightly lecture release flow.

### What changed
- **Gemini image generation added** for lesson visuals using `gemini-3.1-flash-lite-image`.
- The app now serves a **public website** at `/` and the operational dashboard at `/admin`.
- Generated lessons are browsable at `/lessons/<slug>/`.
- Default nightly schedule is **9:00 PM IST**.
- Lesson pages and the academy homepage use a more premium, polished presentation.

### Required environment variables
- `OPENAI_API_KEY` for lesson writing/editorial review
- `GEMINI_API_KEY` for premium lesson image generation

### URLs
- Website home: `http://127.0.0.1:8765/`
- Admin dashboard: `http://127.0.0.1:8765/admin`

If Gemini image generation fails at runtime, Professor OS automatically falls back to the local visual renderer so the lecture pipeline still completes.


## v12.0 — Student Learning Experience

The public Professor OS Academy has been redesigned around the student learning journey.

- Premium lecture detail pages with sticky table of contents and reading progress.
- Browser-local student progress tracking: completed classes, last opened lecture, and saved reading position.
- Continue Learning / resume behavior.
- Category filters across the 60-class curriculum.
- Full curriculum search by title, concepts, category, and summary.
- Tonight's upcoming lecture teaser with a live countdown to the nightly release.
- Cleaner typography, denser spacing, stronger information hierarchy, and more consistent cards.
- Refined responsive/mobile layout with a compact bottom navigation and mobile learning dock.
- Subtle reveal, hover, orb, shimmer, and progress animations with `prefers-reduced-motion` support.
- Existing generated lesson pages are rebuilt automatically at website startup so old lectures inherit the newest student UI without being regenerated by the AI.

Student progress currently uses browser `localStorage`, so it requires no account or database and remains private to that browser. A future account system can replace this storage layer without changing the public learning UX.


## v16.0 — van Lent inspired academy UI

This version translates the editorial and motion principles of vanlent.dev into Professor OS without copying its proprietary source or content.

- Oversized editorial hero typography with numbered rows.
- Horizontal "Selected Classes" storytelling instead of a generic card grid.
- Learning System section inspired by capability/service storytelling.
- Restrained micro-motion, section numbering, and high-contrast typography.
- Student progress, search, filters, nightly countdown, and local resume state remain functional.
- Lecture detail pages now use the same numbered editorial rhythm.


## v17.0 — Saifullah.dev-Inspired System Interface

Professor OS now uses an immersive systems-interface design language inspired by the structural ideas of saifullah.dev: persistent system telemetry, coded navigation, data-stream lecture objects, technical sectors, performance-aware motion, and a custom browser-rendered robotics core. The implementation is original and keeps the existing autonomous nightly generation pipeline, progress tracking, search, filters, Gemini visuals, and Python 3.7-compatible backend.

Run the live academy directly:

```bash
python -m teacher_agent.main
```

The website and scheduler start together. `/admin` is not a separate product interface.


## v18.1 — Learning Operating System UI

Professor OS now uses a persistent OS shell rather than a long dashboard page. The single public interface includes Home, Learn, Library, Tonight, and System applications, a command palette, activity center, runtime telemetry, live scheduler state, an interactive 3D knowledge-core render, browser progress tracking, and an OS-style lesson Reader. The normal command remains `python -m teacher_agent.main`; the website and nightly scheduler start together. `/admin` continues to redirect to the single live Professor OS interface.

### v18.1 visual merge

The v18 Learning OS interaction model is unchanged, but its visual system now inherits the stronger v17 palette: near-black graphite surfaces, neutral gray dividers, off-white typography, acid-green primary actions, pale acid highlights, cyan reserved as a secondary technical accent, and warmer amber/green/red semantic states. This keeps the v18 OS UX while restoring the more distinctive v17 character.


## v18.1 Cloud Deployment

See `FREE_CLOUD_DEPLOY.md` for the free Render + GitHub Actions architecture.
