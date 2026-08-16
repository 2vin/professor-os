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

It shows current class and curriculum position, backend operation, lesson-generation state, network retries, validation/repair activity, visual generation, artifacts, GitHub/LinkedIn stages, event history, errors, preview/publish memory, and the next 4:30 PM IST run.

## Python 3.7 installation

```bash
python3.7 -m venv .linkvenv
source .linkvenv/bin/activate
python -m pip install --upgrade "pip<24.1"
python -m pip install -r requirements.txt
cp .env.example .env
```

At minimum configure `OPENAI_API_KEY`, then run `python -m pytest -v` before starting Professor OS.

## Start the dashboard

```bash
python -m teacher_agent.main --dashboard
```

Open `http://127.0.0.1:8765`. By default the dashboard also activates the daily 4:30 PM IST scheduler.

## Automatic validated source sync

When `AUTO_SYNC_SOURCE=true`, Professor OS watches its application source. A changed source snapshot is pushed to the configured GitHub repository only after `pytest -q` and Python compile checks both pass. `.env`, tokens, logs, local runtime state, virtual environments, caches, and preview content are excluded from source sync.

## Premium Publication Pipeline

Professor OS blocks publication unless the final lesson passes all of these gates:

1. Required lesson structure and Python execution validation.
2. Senior editorial scoring for technical accuracy, pedagogy, clarity, depth, examples, interactivity, code alignment, visual teaching, originality, consistency, and accessibility.
3. Automatic rewrite/re-review when a quality dimension falls below threshold.
4. Optional open-license real-media enrichment when it improves learning.
5. Machine-readable media-license filtering and a saved `MEDIA_CREDITS.md` attribution record.
6. A Professor OS-generated 16:9 LinkedIn cover and professional engineering schematic for visual consistency.
7. A responsive `index.html` canonical lesson page, an `article.html` compatibility copy, and local `linkedin_preview.html`.
8. LinkedIn preflight for title, description, commentary density, hashtags, source URL, alt text, image dimensions, and article-card presentation.
9. A final all-or-nothing publication audit across the exact packaged content.
10. GitHub lesson upload before LinkedIn publishing.
11. LinkedIn publishing only after every gate passes.

## v10.3 — Automatic technical correction

Blocking factual, mathematical, simulation, code-semantic, and internal-consistency findings now trigger a dedicated senior-faculty technical-correction loop instead of an immediate runtime failure. Professor OS sends the exact blocking review back for correction, reruns the full structural/Python validator, then asks the editorial board to verify the corrected result.

`TECHNICAL_QUALITY_REPAIR_ROUNDS=3` controls the repair budget. The correction prompt independently verifies reviewer claims, re-derives disputed equations, distinguishes stability boundaries from response-shape boundaries, fixes actual Python logic, and asks for executable boundary self-checks when appropriate.

If repair attempts are exhausted, the run enters a safe **Publication Hold** state. It is not labeled as an agent-startup crash, the class is not marked complete or published, and the exact blocking reasons remain visible for the next retry.
