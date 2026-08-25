import hashlib
import os
import subprocess
import sys
import threading
from pathlib import Path

from .config import settings
from .github_client import GitHubSourceSync
from .runtime import monitor


INCLUDE_FILES = [
    'README.md', 'requirements.txt', 'curriculum.json', 'Dockerfile',
    'github-actions-example.yml', 'pytest.ini', '.env.example',
]
INCLUDE_DIRS = ['teacher_agent', 'tests']
EXCLUDE_PARTS = {'__pycache__', '.pytest_cache', '.git', '.linkvenv', 'preview'}


def collect_source_files(root=None):
    root = Path(root or '.').resolve()
    result = {}
    for rel in INCLUDE_FILES:
        path = root / rel
        if path.exists() and path.is_file():
            result[rel] = path.read_bytes()
    for directory in INCLUDE_DIRS:
        base = root / directory
        if not base.exists():
            continue
        for path in base.rglob('*'):
            if not path.is_file() or any(part in EXCLUDE_PARTS for part in path.parts):
                continue
            if path.suffix.lower() not in ('.py', '.html', '.md', '.json', '.txt', '.yml', '.yaml', '.ini'):
                continue
            result[str(path.relative_to(root)).replace(os.sep, '/')] = path.read_bytes()
    return result


def source_hash(file_map):
    digest = hashlib.sha256()
    for path in sorted(file_map):
        digest.update(path.encode('utf-8'))
        digest.update(b'\0')
        digest.update(file_map[path])
        digest.update(b'\0')
    return digest.hexdigest()


def run_quality_gate(root=None):
    root = str(Path(root or '.').resolve())
    monitor.source_sync('validating', 'Running pytest validation gate.')
    test = subprocess.run(
        [sys.executable, '-m', 'pytest', '-q'], cwd=root,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    if test.returncode != 0:
        raise RuntimeError('pytest failed; source was NOT pushed.\n' + test.stdout[-4000:])
    monitor.source_sync('validating', 'Tests passed. Running Python compile gate.')
    compile_check = subprocess.run(
        [sys.executable, '-m', 'compileall', '-q', 'teacher_agent', 'tests'], cwd=root,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    if compile_check.returncode != 0:
        raise RuntimeError('compileall failed; source was NOT pushed.\n' + compile_check.stdout[-4000:])
    return {'tests': 'passed', 'compile': 'passed'}


def sync_source_once(root=None):
    if not settings.auto_sync_source:
        monitor.source_sync('skipped', 'Automatic source sync is disabled.')
        return {'changed': False, 'reason': 'disabled'}
    if not (settings.github_token and settings.github_owner and settings.github_repo):
        monitor.source_sync('skipped', 'GitHub source sync is not configured.')
        return {'changed': False, 'reason': 'not_configured'}
    try:
        files = collect_source_files(root)
        digest = source_hash(files)
        run_quality_gate(root)
        monitor.source_sync('syncing', 'Validation passed. Uploading source to GitHub.')
        result = GitHubSourceSync().sync_files(files, digest)
        if result.get('changed'):
            monitor.source_sync('synced', 'Validated source pushed to GitHub.', result.get('commit_sha'))
            monitor.integration('github', True, 'Validated source sync succeeded.')
        else:
            monitor.source_sync('skipped', 'GitHub already has this validated source version.')
            monitor.integration('github', True, 'GitHub source state verified; no changes required.')
        return result
    except Exception as exc:
        monitor.source_sync('error', str(exc))
        monitor.event('warning', 'Code sync failed independently of the teaching run: {0}'.format(exc))
        return {'changed': False, 'reason': 'sync_error', 'error': str(exc)}


class SourceSyncWatcher(object):
    def __init__(self, root=None, interval=None):
        self.root = Path(root or '.').resolve()
        self.interval = int(interval or settings.source_sync_interval)
        self._stop = threading.Event()
        self._thread = None
        self._last_hash = None
        self._lock = threading.Lock()

    def _loop(self):
        while not self._stop.is_set():
            try:
                files = collect_source_files(self.root)
                digest = source_hash(files)
                if digest != self._last_hash:
                    with self._lock:
                        result = sync_source_once(self.root)
                    # Do not acknowledge a failed sync. Keeping _last_hash unchanged makes
                    # the watcher retry the same validated source snapshot on the next cycle.
                    if result.get('reason') != 'sync_error':
                        self._last_hash = digest
                    else:
                        monitor.source_sync('error', 'Code sync will retry automatically on the next interval: {0}'.format(
                            result.get('error', 'unknown GitHub error')))
            except Exception:
                pass
            self._stop.wait(self.interval)

    def start(self):
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name='professor-os-source-sync')
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
