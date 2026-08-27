import json
import mimetypes
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

try:
    from urllib.parse import parse_qs, quote, unquote, urlparse
except ImportError:
    from urlparse import parse_qs, urlparse
    from urllib import quote, unquote

from .article_renderer import render_premium_article
from .config import settings
from .pipeline import RoboticsTeacherAgent, slugify
from .progress import load_progress
from .lesson_chat import (
    LessonChatTutor,
    allow_chat_request,
    extract_chapter,
    sanitize_history,
)
from .runtime import monitor, LOG_PATH, STATE_PATH
from .scheduler import DailyISTScheduler
from .source_sync import SourceSyncWatcher


_scheduler = None
_source_sync_watcher = None
_SITE_TEMPLATE = Path(__file__).parent / 'templates' / 'student_site.html'
_PROJECT_ROOT = Path.cwd().resolve()
_CURRICULUM_PATH = _PROJECT_ROOT / 'curriculum.json'

# Deliberately bumped for the requested full course restart. Old V1 browser
# reading/completion state stays isolated and no longer affects the restarted course.
STUDENT_PROGRESS_KEY = 'professorOSStudentProgressV2'


def _run_agent_thread():
    def target():
        try:
            RoboticsTeacherAgent().run_once()
        except Exception as exc:
            monitor.fail('Agent startup/run failure: {0}'.format(exc))
    thread = threading.Thread(target=target, name='robotics-teacher-run')
    thread.daemon = True
    thread.start()


def start_scheduler():
    global _scheduler
    if _scheduler is not None:
        return _scheduler
    _scheduler = DailyISTScheduler(
        _run_agent_thread,
        hour=settings.nightly_release_hour,
        minute=settings.nightly_release_minute)
    _scheduler.start()
    return _scheduler


def _load_curriculum():
    if not _CURRICULUM_PATH.exists():
        return []
    try:
        data = json.loads(_CURRICULUM_PATH.read_text(encoding='utf-8'))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _resolve_safe_path(raw_path):
    if not raw_path:
        return None
    candidate = Path(unquote(raw_path))
    if not candidate.is_absolute():
        candidate = (_PROJECT_ROOT / candidate).resolve()
    else:
        candidate = candidate.resolve()
    try:
        candidate.relative_to(_PROJECT_ROOT)
    except Exception:
        return None
    if candidate.exists() and candidate.is_file():
        return candidate
    return None


def _artifact_url(path):
    return '/artifact?path=' + quote(str(path))


def _site_lesson_url(slug):
    return '/lessons/{0}/'.format(slug)


def _category_for_class(class_no):
    class_no = int(class_no)
    if class_no <= 5:
        return 'Foundations'
    if class_no <= 13:
        return 'Hardware & Sensors'
    if class_no <= 20:
        return 'Control & Motion'
    if class_no <= 24:
        return 'Probability & Filtering'
    if class_no <= 30:
        return 'Computer Vision'
    if class_no <= 36:
        return 'Localization & Mapping'
    if class_no <= 41:
        return 'Planning'
    if class_no <= 47:
        return 'Manipulation & Dynamics'
    if class_no <= 53:
        return 'Robot Software & Simulation'
    if class_no <= 58:
        return 'Learning & Autonomy'
    return 'Safety & Capstone'


def _reading_minutes(lesson_md):
    if not lesson_md.exists():
        return 0
    try:
        words = len(lesson_md.read_text(encoding='utf-8').split())
        return max(6, int(round(words / 190.0)))
    except Exception:
        return 0


def _lecture_summary(lecture):
    concepts = [x.strip() for x in str(lecture.get('concepts') or '').split(',') if x.strip()]
    if concepts:
        return 'Learn {0} through intuition, worked examples, visuals, and Python labs.'.format(', '.join(concepts[:3]))
    return 'A structured robotics lesson with explanations, visuals, and practical exercises.'


def _lecture_preview(lecture):
    slug = '{0:03d}-{1}'.format(lecture['class_no'], slugify(lecture['title']))
    preview_dir = _PROJECT_ROOT / 'preview' / slug
    lesson_md = preview_dir / 'README.md'
    lesson_html = preview_dir / 'index.html'
    diagram = preview_dir / 'diagram.png'
    hero = preview_dir / 'hero.png'
    podcast = preview_dir / 'podcast.mp3'
    code_dir = preview_dir / 'code'
    code_files = []
    if code_dir.exists():
        for code_path in sorted(code_dir.glob('*.py')):
            code_files.append({
                'name': code_path.name,
                'url': '/lessons/{0}/code/{1}'.format(slug, code_path.name),
            })
    return {
        'slug': slug,
        'preview_dir': str(preview_dir),
        'preview_available': lesson_md.exists(),
        'page_available': lesson_html.exists(),
        'diagram_available': diagram.exists(),
        'hero_available': hero.exists(),
        'podcast_available': podcast.exists(),
        'code_count': len(code_files),
        'category': _category_for_class(lecture['class_no']),
        'summary': _lecture_summary(lecture),
        'reading_minutes': _reading_minutes(lesson_md),
        'lesson_url': _site_lesson_url(slug) if lesson_html.exists() else None,
        'diagram_url': '/lessons/{0}/diagram.png'.format(slug) if diagram.exists() else None,
        'hero_url': '/lessons/{0}/hero.png'.format(slug) if hero.exists() else None,
        'podcast_url': '/lessons/{0}/podcast.mp3'.format(slug) if podcast.exists() else None,
        'code_urls': code_files,
    }


def _lecture_status(lecture, progress, current_class, state_status):
    class_no = lecture['class_no']
    if state_status == 'running' and class_no == current_class:
        return 'active'
    if class_no <= int(progress.get('last_published_class', 0) or 0):
        return 'published'
    if class_no <= int(progress.get('last_generated_class', 0) or 0):
        return 'generated' if lecture.get('preview_available') else 'missing'
    next_class = max(
        int(progress.get('last_generated_class', 0) or 0),
        int(progress.get('last_published_class', 0) or 0)
    ) + 1
    if class_no == next_class:
        return 'next'
    return 'queued'


def _visible_class_limit(progress=None):
    progress = progress or load_progress()
    return max(
        int(progress.get('last_generated_class', 0) or 0),
        int(progress.get('last_published_class', 0) or 0)
    )


def _hide_cached_unreleased_assets(item):
    item['cached_package_present'] = bool(item.get('preview_available') or item.get('page_available'))
    item['preview_available'] = False
    item['page_available'] = False
    item['diagram_available'] = False
    item['hero_available'] = False
    item['podcast_available'] = False
    item['lesson_url'] = None
    item['diagram_url'] = None
    item['hero_url'] = None
    item['podcast_url'] = None
    item['code_urls'] = []
    item['code_count'] = 0
    return item


def _latest_lesson_url(lectures):
    available = [x for x in lectures if x.get('page_available') and x.get('lesson_url')]
    if not available:
        return None
    return available[-1]['lesson_url']


def _state_payload():
    data = monitor.snapshot()
    progress = load_progress()
    data['course_memory'] = progress
    data['course_total'] = len(_load_curriculum())
    data['student_progress_key'] = STUDENT_PROGRESS_KEY
    data['brand'] = {
        'name': 'Professor OS',
        'builder': 'Connect.Vin',
        'version': '18.1',
    }

    integration_health = data.get('integration_health') or {}
    github_health = integration_health.get('github') or {}
    linkedin_health = integration_health.get('linkedin') or {}
    data['integrations'] = {
        'github': {
            'configured': bool(settings.github_token and settings.github_owner and settings.github_repo),
            'enabled': bool(settings.auto_publish or settings.auto_sync_source),
            'connected': bool(github_health.get('connected')),
            'message': github_health.get('message') or 'Not verified in this runtime.',
            'last_checked': github_health.get('last_checked'),
            'label': '{0}/{1}'.format(settings.github_owner or 'owner', settings.github_repo or 'repo'),
        },
        'linkedin': {
            'configured': bool(settings.linkedin_access_token and settings.linkedin_author_urn),
            'enabled': bool(settings.auto_publish),
            'connected': bool(linkedin_health.get('connected')),
            'message': linkedin_health.get('message') or 'Not verified in this runtime.',
            'last_checked': linkedin_health.get('last_checked'),
            'label': settings.linkedin_author_urn or 'Not configured',
        },
    }

    if _scheduler is not None:
        data['scheduler'] = {
            'enabled': True,
            'next_run': _scheduler.next_run_time().isoformat(),
            'timezone': 'Asia/Kolkata',
            'hour': settings.nightly_release_hour,
            'minute': settings.nightly_release_minute,
        }

    curriculum = _load_curriculum()
    visible_limit = _visible_class_limit(progress)
    lectures = []
    for lecture in curriculum:
        item = dict(lecture)
        item.update(_lecture_preview(lecture))
        item['status'] = _lecture_status(item, progress, data.get('current_class'), data.get('status'))
        if int(item.get('class_no') or 0) > visible_limit:
            _hide_cached_unreleased_assets(item)
        lectures.append(item)

    for idx, item in enumerate(lectures):
        previous_item = lectures[idx - 1] if idx > 0 else None
        next_item = lectures[idx + 1] if idx + 1 < len(lectures) else None
        item['previous_lesson_url'] = previous_item.get('lesson_url') if previous_item else None
        item['next_lesson_url'] = next_item.get('lesson_url') if next_item else None

    data['lectures'] = lectures
    category_names = []
    for item in lectures:
        category = item.get('category')
        if category and category not in category_names:
            category_names.append(category)
    data['categories'] = category_names

    upcoming = None
    for item in lectures:
        if item.get('status') in ('next', 'queued'):
            upcoming = dict(item)
            break
    data['upcoming_lecture'] = upcoming

    generated_available = len([
        x for x in lectures
        if x.get('status') in ('generated', 'active') and x.get('preview_available')
    ])
    published_count = len([x for x in lectures if x.get('status') == 'published'])
    missing_count = len([x for x in lectures if x.get('status') == 'missing'])
    data['integrity'] = {
        'generated_available_count': generated_available,
        'published_count': published_count,
        'missing_count': missing_count,
        'healthy': missing_count == 0,
        'message': (
            'All generated lesson packages are present.'
            if missing_count == 0
            else '{0} generated lesson package(s) are missing locally. The next run will regenerate the earliest missing class.'.format(missing_count)
        ),
    }
    data['links'] = {
        'home': '/',
        'admin': '/',
        'latest_lesson': _latest_lesson_url(lectures),
        'runtime_state': _artifact_url(STATE_PATH) if STATE_PATH.exists() else None,
        'agent_log': _artifact_url(LOG_PATH) if LOG_PATH.exists() else None,
        'curriculum': _artifact_url(_CURRICULUM_PATH) if _CURRICULUM_PATH.exists() else None,
    }
    arts = []
    for artifact in data.get('artifacts', []):
        item = dict(artifact)
        resolved = _resolve_safe_path(item.get('path'))
        item['url'] = _artifact_url(resolved or item.get('path')) if resolved else None
        arts.append(item)
    data['artifacts'] = arts
    return data


def _rebuild_existing_lesson_pages():
    curriculum = _load_curriculum()
    visible_limit = _visible_class_limit()
    rebuilt = 0
    for index, lesson in enumerate(curriculum):
        if int(lesson.get('class_no') or 0) > visible_limit:
            continue
        slug = '{0:03d}-{1}'.format(lesson['class_no'], slugify(lesson['title']))
        lesson_dir = _PROJECT_ROOT / 'preview' / slug
        markdown_path = lesson_dir / 'README.md'
        hero_path = lesson_dir / 'hero.png'
        if not markdown_path.exists() or not hero_path.exists():
            continue
        quality_report = None
        quality_path = lesson_dir / 'QUALITY_REPORT.json'
        if quality_path.exists():
            try:
                quality_report = json.loads(quality_path.read_text(encoding='utf-8'))
            except Exception:
                quality_report = None
        previous_item = curriculum[index - 1] if index > 0 else None
        next_item = curriculum[index + 1] if index + 1 < len(curriculum) else None
        previous_slug = ('{0:03d}-{1}'.format(previous_item['class_no'], slugify(previous_item['title'])) if previous_item else None)
        next_slug = ('{0:03d}-{1}'.format(next_item['class_no'], slugify(next_item['title'])) if next_item else None)
        navigation = {
            'previous': ({
                'class_no': previous_item['class_no'],
                'title': previous_item['title'],
                'url': ('/lessons/{0}/'.format(previous_slug)
                        if previous_item['class_no'] <= visible_limit and (_PROJECT_ROOT / 'preview' / previous_slug / 'README.md').exists()
                        else None),
            } if previous_item else None),
            'next': ({
                'class_no': next_item['class_no'],
                'title': next_item['title'],
                'url': ('/lessons/{0}/'.format(next_slug)
                        if next_item['class_no'] <= visible_limit and (_PROJECT_ROOT / 'preview' / next_slug / 'README.md').exists()
                        else None),
            } if next_item else None),
        }
        article_path = lesson_dir / 'index.html'
        render_premium_article(
            markdown_path.read_text(encoding='utf-8'), lesson, article_path,
            hero_filename='hero.png', quality_report=quality_report,
            navigation=navigation)
        (lesson_dir / 'article.html').write_text(article_path.read_text(encoding='utf-8'), encoding='utf-8')
        rebuilt += 1
    if rebuilt:
        monitor.event('success', 'Refreshed {0} existing lesson page(s) with the latest student UI.'.format(rebuilt))
    return rebuilt


def _serve_file(handler, path):
    body = path.read_bytes()
    ctype = mimetypes.guess_type(str(path))[0] or 'application/octet-stream'
    if path.suffix.lower() in ('.md', '.py', '.json', '.txt', '.log', '.yml', '.yaml', '.ini'):
        ctype = 'text/plain; charset=utf-8'
    handler._send(200, body, ctype)



def _safe_static_asset(extra_path):
    base = (_PROJECT_ROOT / 'teacher_agent' / 'static').resolve()
    target = (base / str(extra_path or '')).resolve()

    try:
        target.relative_to(base)
    except Exception:
        return None

    if target.exists() and target.is_file():
        return target

    return None


def _safe_lesson_asset(slug, extra_path):
    base = (_PROJECT_ROOT / 'preview' / slug).resolve()
    target = (base / extra_path).resolve()
    try:
        target.relative_to(base)
    except Exception:
        return None
    if target.exists() and target.is_file():
        return target
    return None


def _class_no_from_slug(slug):
    match = re.match(r'^(\d{3})-', str(slug or ''))
    if not match:
        return None
    try:
        return int(match.group(1))
    except Exception:
        return None


def _lesson_for_chat(class_no):
    try:
        class_no = int(class_no)
    except (TypeError, ValueError):
        return None, None, None

    if class_no <= 0 or class_no > _visible_class_limit():
        return None, None, None

    for lesson in _load_curriculum():
        if int(lesson.get('class_no') or 0) != class_no:
            continue
        slug = '{0:03d}-{1}'.format(class_no, slugify(lesson['title']))
        markdown_path = _PROJECT_ROOT / 'preview' / slug / 'README.md'
        if not markdown_path.exists():
            return None, None, None
        return lesson, slug, markdown_path

    return None, None, None


def _chat_client_key(handler):
    forwarded = str(handler.headers.get('X-Forwarded-For') or '').strip()
    if forwarded:
        return forwarded.split(',')[0].strip()[:160]
    try:
        return str(handler.client_address[0])[:160]
    except Exception:
        return 'unknown'


class DashboardHandler(BaseHTTPRequestHandler):
    server_version = 'ProfessorOS/18.1'

    def log_message(self, fmt, *args):
        return

    def _send(self, status, body, content_type):
        if isinstance(body, str):
            body = body.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status, payload):
        self._send(status, json.dumps(payload).encode('utf-8'), 'application/json; charset=utf-8')

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/':
            try:
                page = _SITE_TEMPLATE.read_text(encoding='utf-8')
                page = page.replace('professorOSStudentProgressV1', STUDENT_PROGRESS_KEY)
            except Exception as exc:
                self._send(500, 'Website template error: {0}'.format(exc), 'text/plain; charset=utf-8')
                return
            self._send(200, page, 'text/html; charset=utf-8')
            return
        if parsed.path == '/admin':
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
            return
        if parsed.path == '/api/state':
            self._json(200, _state_payload())
            return
        if parsed.path == '/api/health':
            self._json(200, {
                'ok': True,
                'python_target': '3.7',
                'mode': 'publish' if settings.auto_publish else 'preview',
                'nightly_release': '{0:02d}:{1:02d} IST'.format(settings.nightly_release_hour, settings.nightly_release_minute),
                'lesson_chat_enabled': bool(settings.lesson_chat_enabled),
                'lesson_chat_configured': True,
                'lesson_chat_provider': settings.lesson_chat_provider,
                'lesson_chat_model': settings.lesson_chat_model,
                'lesson_chat_paid_fallback': False,
                'lesson_chat_server_inference': False,
                'lesson_chat_privacy': 'on-device',
            })
            return
        if parsed.path.startswith('/static/'):
            extra = parsed.path[len('/static/'):]
            target = _safe_static_asset(extra)
            if target:
                _serve_file(self, target)
                return

            self._send(
                404,
                'Static asset not found.',
                'text/plain; charset=utf-8'
            )
            return

        if parsed.path.startswith('/lessons/'):
            parts = [p for p in parsed.path.split('/') if p]
            if len(parts) >= 2:
                slug = parts[1]
                class_no = _class_no_from_slug(slug)
                if class_no is None or class_no > _visible_class_limit():
                    self._send(404, 'Lesson not currently published.', 'text/plain; charset=utf-8')
                    return
                extra = '/'.join(parts[2:]) if len(parts) > 2 else 'index.html'
                target = _safe_lesson_asset(slug, extra)
                if target is None and extra == '':
                    target = _safe_lesson_asset(slug, 'index.html')
                if target is None and parsed.path.endswith('/'):
                    target = _safe_lesson_asset(slug, 'index.html')
                if target:
                    _serve_file(self, target)
                    return
            self._send(404, 'Lesson not found.', 'text/plain; charset=utf-8')
            return
        if parsed.path == '/artifact':
            query = parse_qs(parsed.query or '')
            target = _resolve_safe_path((query.get('path') or [None])[0])
            if not target:
                self._send(404, 'Artifact not found.', 'text/plain; charset=utf-8')
                return
            _serve_file(self, target)
            return
        self._json(404, {'ok': False, 'message': 'Not found'})

    def _read_json_body(self, max_bytes=20000):
        try:
            length = int(self.headers.get('Content-Length') or '0')
        except ValueError:
            raise ValueError('Invalid Content-Length header.')

        if length <= 0:
            raise ValueError('Request body is required.')
        if length > max_bytes:
            raise ValueError('Request body is too large.')

        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode('utf-8'))
        except Exception:
            raise ValueError('Request body must be valid JSON.')

        if not isinstance(payload, dict):
            raise ValueError('Request body must be one JSON object.')
        return payload

    def _handle_lesson_chat(self):
        # Deliberately no server-side LLM inference. The lesson UI runs an open
        # Qwen model locally in the student's browser, so there is no API bill.
        self._json(410, {
            'ok': False,
            'message': (
                'Professor OS Tutor now runs locally in the browser. '
                'This server endpoint is permanently disabled.'
            ),
            'provider': 'qwen_on_device',
            'server_inference': False,
            'paid_fallback_used': False,
        })

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == '/api/lesson-chat':
            self._handle_lesson_chat()
            return

        if parsed.path != '/api/run':
            self._json(404, {'ok': False, 'message': 'Not found'})
            return
        if not settings.enable_manual_run:
            self._json(403, {'ok': False, 'message': 'Manual generation is disabled on this deployment.'})
            return
        state = monitor.snapshot()
        if state.get('status') == 'running':
            self._json(409, {'ok': False, 'message': 'Teacher agent is already running.'})
            return
        _run_agent_thread()
        self._json(202, {'ok': True, 'message': 'Teacher agent started.'})


def _bootstrap_live_generation():
    state = monitor.snapshot()
    if state.get('status') == 'running':
        return False
    progress = load_progress()
    generated = int(progress.get('last_generated_class', 0) or 0)
    missing = False
    curriculum = _load_curriculum()
    if curriculum and generated > 0:
        for lecture in curriculum[:generated]:
            preview = _lecture_preview(lecture)
            if not preview.get('preview_available') or not preview.get('hero_available'):
                missing = True
                break
    if generated == 0 or missing:
        _run_agent_thread()
        monitor.event('info', 'Bootstrapped live generation on website start.')
        return True
    return False


def run_dashboard():
    global _source_sync_watcher
    _rebuild_existing_lesson_pages()
    if settings.dashboard_schedule:
        start_scheduler()
    if settings.auto_bootstrap_generation:
        _bootstrap_live_generation()
    if settings.auto_sync_source:
        _source_sync_watcher = SourceSyncWatcher()
        _source_sync_watcher.start()
    address = (settings.dashboard_host, settings.dashboard_port)
    server = ThreadingHTTPServer(address, DashboardHandler)
    monitor.event('info', 'Professor OS website started at http://{0}:{1}'.format(*address))
    print('Professor OS live website: http://{0}:{1}'.format(*address))
    print('Built by Connect.Vin')
    try:
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        if _scheduler is not None:
            _scheduler.stop()
        if _source_sync_watcher is not None:
            _source_sync_watcher.stop()
        monitor.scheduler(False, None, settings.timezone)
