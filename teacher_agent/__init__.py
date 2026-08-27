"""Professor OS package bootstrap."""

# Install the podcast renderer/publication hooks before pipeline.py imports the
# renderer and publication gate functions. The hooks are inert unless podcast
# files exist or PODCAST_ENABLED=true.
from .podcast import install_runtime_hooks

install_runtime_hooks()
