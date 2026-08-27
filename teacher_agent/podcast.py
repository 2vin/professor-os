import datetime
import html
import json
import os
import re
from pathlib import Path

from .config import settings
from .http_utils import request_with_retry
from .runtime import monitor


PODCAST_FILENAME = 'podcast.mp3'
PODCAST_META_FILENAME = 'PODCAST.json'
PODCAST_TRANSCRIPT_FILENAME = 'podcast_transcript.txt'
TTS_URL = 'https://api.openai.com/v1/audio/speech'
_UI_START = '<!-- PROFESSOR_OS_PODCAST_START -->'
_UI_END = '<!-- PROFESSOR_OS_PODCAST_END -->'
_STYLE_START = '/* PROFESSOR_OS_PODCAST_STYLE_START */'
_STYLE_END = '/* PROFESSOR_OS_PODCAST_STYLE_END */'


def _pytest_running():
    # The nightly workflow enables PODCAST_REQUIRED for real generation, but pytest
    # must stay deterministic and must never spend TTS credits. Pytest exposes this
    # variable while each test is executing.
    return bool(os.getenv('PYTEST_CURRENT_TEST'))


def _word_count(text):
    return len([item for item in re.split(r'\s+', str(text or '').strip()) if item])


def _trim_script(text, max_words):
    text = str(text or '').strip()
    if not text:
        return text

    words = text.split()
    if len(words) <= max_words:
        return text

    clipped = ' '.join(words[:max_words])
    # Prefer ending at a sentence boundary near the word limit.
    boundary = max(clipped.rfind('.'), clipped.rfind('?'), clipped.rfind('!'))
    if boundary >= int(len(clipped) * 0.72):
        clipped = clipped[:boundary + 1]
    else:
        clipped = clipped.rstrip(' ,;:-') + '.'
    return clipped


def _podcast_prompt(markdown, lesson):
    return (
        'Create a single-host educational podcast script from the final Professor OS lesson below.\n\n'
        'Audience: a motivated beginner who may be listening while walking or commuting.\n'
        'Length: about 850-1,050 spoken words. Never exceed 1,100 words.\n'
        'Tone: warm, precise, calm, technically trustworthy, and conversational without hype.\n\n'
        'Requirements:\n'
        '- begin with: "Welcome to Professor OS." and identify the class number and title;\n'
        '- preserve the lesson\'s factual meaning and terminology;\n'
        '- explain the central idea, one memorable worked example, the most important engineering caveat, and the practical takeaway;\n'
        '- include one short "pause and predict" question and reveal the answer after a brief verbal beat;\n'
        '- mention the Python lab conceptually, but DO NOT read source code line by line;\n'
        '- do not read Markdown syntax, image filenames, URLs, citations, tables, or JSON aloud;\n'
        '- do not invent facts, examples, measurements, sources, or claims that are not supported by the lesson;\n'
        '- keep mathematical notation speakable in plain English;\n'
        '- end with a concise recap and a one-sentence preview of the next class if the lesson provides one;\n'
        '- output plain spoken text only: no Markdown headings, bullets, stage directions, speaker labels, or commentary.\n\n'
        'LESSON IDENTITY:\n'
        'Class {0}: {1}\n\n'
        'FINAL LESSON:\n{2}'
    ).format(
        lesson.get('class_no', ''),
        lesson.get('title', ''),
        markdown
    )


def build_podcast_script(markdown, lesson, writer=None):
    if writer is None:
        from .lesson_writer import LessonWriter
        writer = LessonWriter()

    instructions = (
        'You are the Professor OS audio editor. Convert a validated robotics lesson into a '
        'high-quality single-host educational podcast script. Preserve technical accuracy, '
        'make it natural to hear, and return only the spoken script.'
    )
    script = writer._call_openai(
        instructions,
        _podcast_prompt(markdown, lesson)
    )
    script = _trim_script(script, settings.podcast_script_max_words)
    if _word_count(script) < 350:
        raise RuntimeError('Podcast script is unexpectedly short.')
    return script


def _looks_like_mp3(data):
    if not data or len(data) < 4:
        return False
    if data[:3] == b'ID3':
        return True
    return data[0] == 0xff and (data[1] & 0xe0) == 0xe0


def synthesize_podcast(script, output_path):
    if not settings.openai_api_key:
        raise RuntimeError('OPENAI_API_KEY is required for podcast narration.')

    payload = {
        'model': settings.podcast_tts_model,
        'voice': settings.podcast_voice,
        'input': script,
        'response_format': 'mp3',
    }

    # GPT-4o Mini TTS supports delivery instructions. Keep a fallback for any
    # alternate speech model that rejects this field.
    if str(settings.podcast_tts_model).startswith('gpt-4o-mini-tts'):
        payload['instructions'] = (
            'Speak as an expert robotics teacher hosting a premium educational podcast. '
            'Use a calm, natural pace, clear articulation, short pauses between ideas, and '
            'slightly more emphasis for predictions, equations, and key takeaways. '
            'Do not sound like an advertisement.'
        )

    headers = {
        'Authorization': 'Bearer ' + settings.openai_api_key,
        'Content-Type': 'application/json',
        'Accept': 'audio/mpeg',
    }

    response = request_with_retry(
        'POST',
        TTS_URL,
        headers=headers,
        json=payload,
        timeout=settings.podcast_timeout,
        max_attempts=settings.api_max_attempts,
        base_delay=settings.api_retry_base_delay,
    )

    # Some speech models may reject narration instructions. Retry once without
    # them instead of failing a valid TTS configuration.
    if response.status_code == 400 and 'instructions' in payload:
        body = response.text.lower() if response.text else ''
        if 'instruction' in body or 'unsupported' in body or 'unknown' in body:
            retry_payload = dict(payload)
            retry_payload.pop('instructions', None)
            response = request_with_retry(
                'POST',
                TTS_URL,
                headers=headers,
                json=retry_payload,
                timeout=settings.podcast_timeout,
                max_attempts=settings.api_max_attempts,
                base_delay=settings.api_retry_base_delay,
            )

    try:
        response.raise_for_status()
    except Exception:
        body = response.text[-2000:] if response.text else '(binary or empty response body)'
        raise RuntimeError(
            'OpenAI podcast TTS returned HTTP {0}: {1}'.format(
                response.status_code,
                body
            )
        )

    audio = response.content or b''
    if len(audio) < 10000:
        raise RuntimeError(
            'OpenAI podcast audio is suspiciously small: {0} bytes.'.format(len(audio))
        )
    if not _looks_like_mp3(audio):
        raise RuntimeError('OpenAI podcast response does not look like an MP3 file.')

    output_path = Path(output_path)
    output_path.write_bytes(audio)
    return output_path


def load_podcast_metadata(output_dir):
    path = Path(output_dir) / PODCAST_META_FILENAME
    audio_path = Path(output_dir) / PODCAST_FILENAME
    if not path.exists() or not audio_path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    return data


def ensure_podcast_package(markdown, lesson, output_dir, writer=None, force=False):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    existing = load_podcast_metadata(output_dir)
    if existing and not force:
        return existing

    if not settings.podcast_enabled:
        return None

    script = build_podcast_script(markdown, lesson, writer=writer)
    transcript_path = output_dir / PODCAST_TRANSCRIPT_FILENAME
    transcript_path.write_text(script + '\n', encoding='utf-8')

    audio_path = output_dir / PODCAST_FILENAME
    synthesize_podcast(script, audio_path)

    words = _word_count(script)
    estimated_minutes = max(1, int(round(words / 150.0)))
    metadata = {
        'filename': PODCAST_FILENAME,
        'transcript_filename': PODCAST_TRANSCRIPT_FILENAME,
        'class_no': int(lesson.get('class_no') or 0),
        'title': str(lesson.get('title') or ''),
        'script_words': words,
        'estimated_minutes': estimated_minutes,
        'tts_model': settings.podcast_tts_model,
        'voice': settings.podcast_voice,
        'synthetic_narration': True,
        'generated_at_utc': datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z',
    }

    meta_path = output_dir / PODCAST_META_FILENAME
    meta_path.write_text(json.dumps(metadata, indent=2), encoding='utf-8')

    try:
        monitor.artifact('podcast', audio_path, 'Downloadable Professor OS podcast MP3')
        monitor.artifact('podcast', meta_path, 'Podcast generation metadata')
    except Exception:
        pass

    return metadata


def _download_name(metadata):
    class_no = int((metadata or {}).get('class_no') or 0)
    title = str((metadata or {}).get('title') or 'lesson').lower()
    slug = re.sub(r'[^a-z0-9]+', '-', title).strip('-') or 'lesson'
    return 'professor-os-class-{0:02d}-{1}.mp3'.format(class_no, slug)


def inject_podcast_ui(html_path, metadata):
    html_path = Path(html_path)
    if not html_path.exists() or not metadata:
        return html_path

    text = html_path.read_text(encoding='utf-8')

    # Idempotent cleanup for pages rebuilt multiple times by the dashboard.
    text = re.sub(
        re.escape(_UI_START) + r'.*?' + re.escape(_UI_END),
        '',
        text,
        flags=re.S
    )
    text = re.sub(
        re.escape(_STYLE_START) + r'.*?' + re.escape(_STYLE_END),
        '',
        text,
        flags=re.S
    )

    minutes = int(metadata.get('estimated_minutes') or 0)
    title = html.escape(str(metadata.get('title') or 'Professor OS lesson'))
    filename = html.escape(str(metadata.get('filename') or PODCAST_FILENAME), quote=True)
    download_name = html.escape(_download_name(metadata), quote=True)

    css = '''
{0}
.podcast-strip{{margin-top:16px;padding:0;overflow:hidden}}
.podcast-inner{{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:18px;align-items:center;padding:18px 20px;background:radial-gradient(circle at 88% 50%,rgba(202,255,79,.10),transparent 28%),linear-gradient(135deg,#0d1013,#0a0d0f)}}
.podcast-copy{{display:grid;gap:7px;min-width:0}}.podcast-kicker{{font-size:8px;letter-spacing:.14em;text-transform:uppercase;color:var(--acid)}}.podcast-copy h2{{margin:0;font-size:20px;letter-spacing:-.025em}}.podcast-copy p{{margin:0;color:var(--muted);font-size:10px;line-height:1.55}}
.podcast-controls{{display:grid;grid-template-columns:minmax(240px,360px) auto;gap:10px;align-items:center}}.podcast-controls audio{{width:100%;height:38px;accent-color:var(--acid)}}.podcast-download{{display:inline-flex;align-items:center;justify-content:center;white-space:nowrap;padding:11px 13px;border-radius:11px;background:linear-gradient(135deg,var(--acid),var(--acid2));color:#111;font-size:8px;font-weight:900;letter-spacing:.09em;text-transform:uppercase}}
@media(max-width:900px){{.podcast-inner{{grid-template-columns:1fr}}.podcast-controls{{grid-template-columns:1fr auto}}}}@media(max-width:560px){{.podcast-controls{{grid-template-columns:1fr}}.podcast-inner{{padding:16px}}}}
{1}
'''.format(_STYLE_START, _STYLE_END)

    card = '''
{start}
<section class="window podcast-strip" id="professorOSPodcast" aria-label="Professor OS podcast">
  <div class="podcast-inner">
    <div class="podcast-copy">
      <span class="podcast-kicker">Listen anywhere</span>
      <h2>Class podcast · {title}</h2>
      <p>~{minutes} min · AI-generated narration · Play here or download the MP3 for offline listening.</p>
    </div>
    <div class="podcast-controls">
      <audio controls preload="metadata"><source src="{filename}" type="audio/mpeg">Your browser does not support audio playback.</audio>
      <a class="podcast-download" href="{filename}" download="{download_name}">↓ Download podcast</a>
    </div>
  </div>
</section>
{end}
'''.format(
        start=_UI_START,
        end=_UI_END,
        title=title,
        minutes=minutes,
        filename=filename,
        download_name=download_name,
    )

    if '</style>' in text:
        text = text.replace('</style>', css + '\n</style>', 1)

    anchor = '<div class="reader">'
    if anchor in text:
        text = text.replace(anchor, card + '\n' + anchor, 1)
    elif '</header>' in text:
        text = text.replace('</header>', '</header>\n' + card, 1)
    else:
        text = card + text

    # Add a compact jump link in the top action area when the premium reader UI is present.
    top = '<div class="top-actions">'
    if top in text and 'href="#professorOSPodcast"' not in text:
        text = text.replace(
            top,
            top + '<a class="pill" href="#professorOSPodcast">♫ Podcast</a>',
            1
        )

    html_path.write_text(text, encoding='utf-8')
    return html_path


def validate_podcast_package(output_dir):
    output_dir = Path(output_dir)
    errors = []
    audio_path = output_dir / PODCAST_FILENAME
    meta_path = output_dir / PODCAST_META_FILENAME
    article_path = output_dir / 'index.html'

    if not audio_path.exists():
        errors.append('Required podcast audio is missing: {0}'.format(audio_path))
    else:
        data = audio_path.read_bytes()
        if len(data) < 10000:
            errors.append('Podcast MP3 is suspiciously small: {0} bytes.'.format(len(data)))
        elif not _looks_like_mp3(data):
            errors.append('Podcast file does not have a valid MP3 signature.')

    if not meta_path.exists():
        errors.append('Required podcast metadata is missing: {0}'.format(meta_path))
    else:
        try:
            metadata = json.loads(meta_path.read_text(encoding='utf-8'))
            if not metadata.get('synthetic_narration'):
                errors.append('PODCAST.json must identify the narration as synthetic.')
            if not metadata.get('tts_model') or not metadata.get('voice'):
                errors.append('PODCAST.json is missing TTS model/voice metadata.')
        except Exception as exc:
            errors.append('PODCAST.json is invalid: {0}'.format(exc))

    if not article_path.exists():
        errors.append('Podcast UI cannot be verified because index.html is missing.')
    else:
        page = article_path.read_text(encoding='utf-8')
        if 'id="professorOSPodcast"' not in page:
            errors.append('Rendered lesson is missing the podcast player section.')
        if PODCAST_FILENAME not in page:
            errors.append('Rendered lesson does not reference podcast.mp3.')
        if 'download=' not in page:
            errors.append('Rendered lesson is missing the podcast download action.')
        if 'AI-generated narration' not in page:
            errors.append('Rendered lesson is missing the synthetic narration disclosure.')

    return errors


def install_runtime_hooks():
    """Patch the existing renderer/gate without duplicating their large source files."""
    from . import article_renderer
    from . import publication_gate

    if not getattr(article_renderer.render_premium_article, '_professor_os_podcast_wrapped', False):
        original_render = article_renderer.render_premium_article

        def render_with_podcast(
                markdown,
                lesson,
                output_path,
                hero_filename='hero.png',
                quality_report=None,
                navigation=None):
            output_path = Path(output_path)
            output_dir = output_path.parent
            metadata = load_podcast_metadata(output_dir)

            if metadata is None and settings.podcast_enabled and not _pytest_running():
                try:
                    metadata = ensure_podcast_package(
                        markdown,
                        lesson,
                        output_dir,
                        writer=None,
                        force=False
                    )
                except Exception as exc:
                    if settings.podcast_required:
                        raise RuntimeError('Required podcast generation failed: {0}'.format(exc))
                    monitor.event('warning', 'Optional podcast generation failed: {0}'.format(exc))

            result = original_render(
                markdown,
                lesson,
                output_path,
                hero_filename=hero_filename,
                quality_report=quality_report,
                navigation=navigation
            )

            if metadata and (output_dir / PODCAST_FILENAME).exists():
                inject_podcast_ui(output_path, metadata)
            return result

        render_with_podcast._professor_os_podcast_wrapped = True
        article_renderer.render_premium_article = render_with_podcast

    if not getattr(publication_gate.final_publication_gate, '_professor_os_podcast_wrapped', False):
        original_gate = publication_gate.final_publication_gate

        def gate_with_podcast(
                lesson,
                output_dir,
                quality_report,
                linkedin_preflight,
                media_result,
                code_paths):
            gate = original_gate(
                lesson,
                output_dir,
                quality_report,
                linkedin_preflight,
                media_result,
                code_paths
            )

            output_dir = Path(output_dir)
            podcast_errors = validate_podcast_package(output_dir)
            podcast_exists = (output_dir / PODCAST_FILENAME).exists()

            podcast_required = bool(settings.podcast_required and not _pytest_running())

            if podcast_required:
                gate.setdefault('checks', {})['podcast'] = not podcast_errors
                if podcast_errors:
                    gate.setdefault('errors', []).extend(podcast_errors)
                    gate['passed'] = False
            elif podcast_exists:
                gate.setdefault('checks', {})['podcast'] = not podcast_errors
                if podcast_errors:
                    gate.setdefault('warnings', []).extend(podcast_errors)

            gate['podcast'] = {
                'required': bool(podcast_required),
                'available': bool(podcast_exists),
                'filename': PODCAST_FILENAME if podcast_exists else None,
            }
            gate['message'] = (
                'Publication package passed every final gate.'
                if gate.get('passed')
                else 'Publication blocked by {0} final issue(s).'.format(
                    len(gate.get('errors') or [])
                )
            )
            (output_dir / 'PUBLICATION_GATE.json').write_text(
                json.dumps(gate, indent=2),
                encoding='utf-8'
            )
            return gate

        gate_with_podcast._professor_os_podcast_wrapped = True
        publication_gate.final_publication_gate = gate_with_podcast
