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
4. Optional Wikimedia Commons enrichment only when an external visual/video genuinely improves learning.
5. Machine-readable media-license filtering and a saved `MEDIA_CREDITS.md` attribution record.
6. A Professor OS-generated 16:9 LinkedIn cover and teaching concept map for visual consistency.
7. A responsive `index.html` canonical lesson page, an `article.html` compatibility copy, and local `linkedin_preview.html`.
8. LinkedIn preflight for title, description, commentary density, hashtags, source URL, alt text, image dimensions, and article-card presentation.
9. A final all-or-nothing publication audit across the exact packaged content.
10. GitHub lesson upload before LinkedIn publishing.
11. LinkedIn publishing only after every gate passes.

A typical premium lesson package includes `README.md`, `index.html`, `article.html`, `hero.png`, `diagram.png`, `QUALITY_REPORT.json`, `LINKEDIN_PREFLIGHT.json`, `PUBLICATION_GATE.json`, `linkedin_package.json`, `linkedin_preview.html`, `MEDIA_CREDITS.md`, optional license-verified media, and separately validated Python labs.

### Media policy

Professor OS-generated visuals remain the primary design language. External media is optional. The automated curator currently uses Wikimedia Commons because file pages expose machine-readable license, author, attribution, restriction, and provenance metadata. The automated path accepts public-domain, CC0, and simple CC BY material with usable attribution metadata, while rejecting non-free, NC, ND, ShareAlike, restricted, or insufficiently attributed candidates.

### LinkedIn presentation

LinkedIn controls its final platform font. Professor OS does not use fake Unicode fonts. It validates professional plain-text typography, paragraph rhythm, title/description lengths, focused hashtags, accessibility alt text, a consistent 16:9 thumbnail, and a local article-card approximation before publishing.

## Final Publication Gate

Before any LinkedIn upload, Professor OS performs one last audit of editorial approval, structural/code validation, code-lab presence, 16:9 visual resolution, responsive article HTML, typography declarations, placeholder removal, media-license provenance, and LinkedIn preflight. The result is stored in `PUBLICATION_GATE.json`. If any blocking item fails, GitHub lesson publishing and LinkedIn publishing are stopped.
