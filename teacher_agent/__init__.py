"""Professor OS package bootstrap."""

# Install the podcast renderer/publication hooks before pipeline.py imports the
# renderer and publication gate functions. The hooks are inert unless podcast
# files exist or PODCAST_ENABLED=true.
from .podcast import install_runtime_hooks

install_runtime_hooks()

# The quality duplicate detector must evaluate teaching prose only. This guard
# removes fenced Python before checking repeated paragraphs, preventing similar
# control-loop code from being mistaken for duplicated lesson prose.
from .quality_duplicate_guard import install_runtime_hook

install_runtime_hook()
