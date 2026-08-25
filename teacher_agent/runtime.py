import json
import os
import threading
from datetime import datetime
from pathlib import Path


STATE_PATH = Path('.robotics_teacher_runtime.json')
LOG_PATH = Path('teacher_agent.log')


def _now():
    return datetime.now().astimezone().isoformat()


class RuntimeMonitor(object):
    def __init__(self):
        self._lock = threading.RLock()
        self._state = self._default_state()
        self._load_existing()

    def _default_state(self):
        return {
            'status': 'idle',
            'run_id': None,
            'started_at': None,
            'finished_at': None,
            'current_class': None,
            'current_title': None,
            'course_total': 0,
            'mode': 'preview',
            'current_step': 'Ready',
            'step_detail': 'Waiting for the next class.',
            'last_error': None,
            'publication_hold': {'active': False, 'reason': '', 'attempts': 0},
            'retry': {'attempt': 0, 'max_attempts': 0, 'delay_seconds': 0},
            'steps': [],
            'events': [],
            'artifacts': [],
            'scheduler': {'enabled': False, 'next_run': None, 'timezone': 'Asia/Kolkata'},
            'source_sync': {'status': 'idle', 'message': 'Waiting for source changes.', 'last_commit': None, 'last_sync': None},
            'quality': {'passed': None, 'overall_score': None, 'message': 'Not reviewed yet.'},
            'linkedin_preflight': {'passed': None, 'errors': [], 'warnings': [], 'message': 'Not checked yet.'},
            'integration_health': {
                'github': {'connected': False, 'message': 'Not verified in this runtime.', 'last_checked': None},
                'linkedin': {'connected': False, 'message': 'Not verified in this runtime.', 'last_checked': None},
            },
        }

    def _load_existing(self):
        if not STATE_PATH.exists():
            return
        try:
            data = json.loads(STATE_PATH.read_text(encoding='utf-8'))
            if isinstance(data, dict):
                self._state.update(data)
                self._state['status'] = 'idle'
                self._state['current_step'] = 'Ready'
                self._state['step_detail'] = 'Dashboard restarted. Waiting for the next class.'
        except Exception:
            pass

    def _persist(self):
        tmp = STATE_PATH.with_suffix('.tmp')
        tmp.write_text(json.dumps(self._state, indent=2), encoding='utf-8')
        os.replace(str(tmp), str(STATE_PATH))

    def _append_log(self, level, message):
        line = '[{0}] {1}: {2}\n'.format(_now(), level.upper(), message)
        try:
            with LOG_PATH.open('a', encoding='utf-8') as handle:
                handle.write(line)
        except Exception:
            pass

    def snapshot(self):
        with self._lock:
            return json.loads(json.dumps(self._state))

    def reset_run(self, run_id, class_no, title, total, mode, steps):
        with self._lock:
            scheduler = self._state.get('scheduler', {})
            self._state = self._default_state()
            self._state['scheduler'] = scheduler
            self._state.update({
                'status': 'running',
                'run_id': run_id,
                'started_at': _now(),
                'current_class': class_no,
                'current_title': title,
                'course_total': total,
                'mode': mode,
                'current_step': 'Boot',
                'step_detail': 'Preparing the robotics teacher agent.',
                'steps': [
                    {'id': step_id, 'label': label, 'status': 'pending', 'detail': ''}
                    for step_id, label in steps
                ],
            })
            self._persist()
        self.event('info', 'Run started for Class {0}: {1}'.format(class_no, title))

    def step(self, step_id, detail='', status='running'):
        with self._lock:
            for item in self._state['steps']:
                if item['id'] == step_id:
                    item['status'] = status
                    item['detail'] = detail
                    self._state['current_step'] = item['label']
                    self._state['step_detail'] = detail
                    break
            self._persist()
        if detail:
            self.event('info', detail, persist=False)

    def complete_step(self, step_id, detail=''):
        self.step(step_id, detail=detail, status='complete')

    def fail_step(self, step_id, detail):
        self.step(step_id, detail=detail, status='error')
        with self._lock:
            self._state['last_error'] = detail
            self._persist()
        self.event('error', detail, persist=False)

    def retry(self, attempt, max_attempts, delay_seconds, message):
        with self._lock:
            self._state['retry'] = {
                'attempt': attempt,
                'max_attempts': max_attempts,
                'delay_seconds': delay_seconds,
            }
            self._state['step_detail'] = message
            self._persist()
        self.event('warning', message, persist=False)

    def artifact(self, kind, path, label):
        with self._lock:
            item = {'kind': kind, 'path': str(path), 'label': label, 'time': _now()}
            self._state['artifacts'].append(item)
            self._state['artifacts'] = self._state['artifacts'][-30:]
            self._persist()
        self.event('success', 'Created {0}: {1}'.format(label, path), persist=False)

    def event(self, level, message, persist=True):
        with self._lock:
            self._state['events'].append({'time': _now(), 'level': level, 'message': message})
            self._state['events'] = self._state['events'][-120:]
            if persist:
                self._persist()
        self._append_log(level, message)

    def finish(self, message):
        with self._lock:
            self._state['status'] = 'complete'
            self._state['finished_at'] = _now()
            self._state['current_step'] = 'Complete'
            self._state['step_detail'] = message
            self._state['retry'] = {'attempt': 0, 'max_attempts': 0, 'delay_seconds': 0}
            self._persist()
        self.event('success', message, persist=False)


    def hold(self, message, attempts=0):
        with self._lock:
            self._state['status'] = 'blocked'
            self._state['finished_at'] = _now()
            self._state['last_error'] = None
            self._state['current_step'] = 'Publication Hold'
            self._state['step_detail'] = message
            self._state['publication_hold'] = {
                'active': True,
                'reason': message,
                'attempts': int(attempts or 0),
            }
            self._persist()
        self.event('warning', message, persist=False)

    def fail(self, message):
        with self._lock:
            self._state['status'] = 'error'
            self._state['finished_at'] = _now()
            self._state['last_error'] = message
            self._state['current_step'] = 'Error'
            self._state['step_detail'] = message
            self._persist()
        self.event('error', message, persist=False)



    def quality(self, report):
        ai = (report or {}).get('ai') or {}
        with self._lock:
            self._state['quality'] = {
                'passed': bool((report or {}).get('passed')),
                'overall_score': ai.get('overall_score'),
                'dimensions': ai.get('dimensions') or {},
                'weak_dimensions': [
                    {'name': name, 'score': score}
                    for name, score in (ai.get('dimensions') or {}).items()
                    if int(score) < int(((report or {}).get('thresholds') or {}).get('dimension', 80))
                ],
                'blocking_issues': ai.get('blocking_issues') or [],
                'static_errors': ((report or {}).get('static') or {}).get('errors') or [],
                'rewrite_rounds_used': (report or {}).get('rewrite_rounds_used', 0),
                'message': ('Premium quality gate passed.' if (report or {}).get('passed')
                            else 'Premium quality gate requires attention.'),
            }
            self._persist()

    def linkedin_preflight(self, report):
        with self._lock:
            self._state['linkedin_preflight'] = {
                'passed': bool((report or {}).get('passed')),
                'errors': (report or {}).get('errors') or [],
                'warnings': (report or {}).get('warnings') or [],
                'commentary_length': (report or {}).get('commentary_length'),
                'thumbnail_width': (report or {}).get('thumbnail_width'),
                'thumbnail_height': (report or {}).get('thumbnail_height'),
                'message': ('LinkedIn preflight passed.' if (report or {}).get('passed')
                            else 'LinkedIn preflight blocked publishing.'),
            }
            self._persist()

    def integration(self, name, connected, message=''):
        with self._lock:
            health = self._state.setdefault('integration_health', {})
            health[name] = {
                'connected': bool(connected),
                'message': message or ('Connected.' if connected else 'Connection not verified.'),
                'last_checked': _now(),
            }
            self._persist()
        self.event('success' if connected else 'warning',
                   '{0} integration: {1}'.format(name.title(), message or ('connected' if connected else 'not connected')),
                   persist=False)

    def source_sync(self, status, message='', last_commit=None):
        with self._lock:
            previous = self._state.get('source_sync', {})
            self._state['source_sync'] = {
                'status': status,
                'message': message,
                'last_commit': last_commit if last_commit is not None else previous.get('last_commit'),
                'last_sync': _now() if status in ('synced', 'skipped', 'error') else previous.get('last_sync'),
            }
            self._persist()
        level = 'success' if status == 'synced' else ('error' if status == 'error' else 'info')
        if message:
            self.event(level, 'Source sync: ' + message, persist=False)

    def scheduler(self, enabled, next_run, timezone):
        with self._lock:
            self._state['scheduler'] = {
                'enabled': bool(enabled),
                'next_run': next_run.isoformat() if next_run else None,
                'timezone': timezone,
            }
            self._persist()


monitor = RuntimeMonitor()
