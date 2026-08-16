# Professor OS — Robotics Teacher Agent (Python 3.7)

**Built by Connect.Vin**

A sequential autonomous robotics teacher for Python 3.7. It generates one curriculum-linked class at a time, validates the lesson and runnable Python examples, creates local lesson artifacts, optionally publishes them to GitHub and LinkedIn, and exposes the entire backend workflow on a live single-page local dashboard.

## Automatic validated source sync

When `AUTO_SYNC_SOURCE=true`, Professor OS watches its application source. A changed source snapshot is pushed to the configured GitHub repository only after `pytest -q` and Python compile checks both pass. `.env`, tokens, logs, local runtime state, virtual environments, caches, and preview content are excluded from source sync.
