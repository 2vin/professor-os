import json
from pathlib import Path

from .config import settings
from .podcast import (
    PODCAST_FILENAME,
    ensure_podcast_package,
    inject_podcast_ui,
    load_podcast_metadata,
)
from .progress import load_progress
from .runtime import monitor


def _slugify(text):
    import re
    return re.sub(r'[^a-z0-9]+', '-', str(text).lower()).strip('-')


def backfill_missing_podcasts(curriculum_path='curriculum.json'):
    if not settings.podcast_enabled:
        print('Podcast generation disabled; backfill skipped.')
        return 0

    curriculum_file = Path(curriculum_path)
    if not curriculum_file.exists():
        raise RuntimeError('Curriculum file not found: {0}'.format(curriculum_file))

    curriculum = json.loads(curriculum_file.read_text(encoding='utf-8'))
    progress = load_progress()
    published_until = int(progress.get('last_published_class', 0) or 0)
    max_items = int(settings.podcast_backfill_max)

    if published_until <= 0 or max_items <= 0:
        print('No published podcast backfill required.')
        return 0

    from .lesson_writer import LessonWriter
    writer = None
    generated = 0

    for lesson in curriculum:
        class_no = int(lesson.get('class_no') or 0)
        if class_no <= 0 or class_no > published_until:
            continue

        slug = '{0:03d}-{1}'.format(class_no, _slugify(lesson.get('title', 'lesson')))
        output_dir = Path('preview') / slug
        markdown_path = output_dir / 'README.md'
        if not markdown_path.exists():
            continue

        metadata = load_podcast_metadata(output_dir)
        if metadata is None:
            if generated >= max_items:
                break
            if writer is None:
                writer = LessonWriter()
            monitor.event(
                'info',
                'Backfilling podcast download for published Class {0}.'.format(class_no)
            )
            metadata = ensure_podcast_package(
                markdown_path.read_text(encoding='utf-8'),
                lesson,
                output_dir,
                writer=writer,
                force=False
            )
            generated += 1

        if metadata and (output_dir / PODCAST_FILENAME).exists():
            for name in ('index.html', 'article.html'):
                page = output_dir / name
                if page.exists():
                    inject_podcast_ui(page, metadata)

    print('Professor OS podcast backfill generated {0} podcast(s).'.format(generated))
    return generated


def main():
    backfill_missing_podcasts()


if __name__ == '__main__':
    main()
