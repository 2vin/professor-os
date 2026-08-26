import json
import re
import threading
import uuid
from pathlib import Path

from .article_renderer import render_linkedin_preview, render_premium_article
from .config import settings
from .diagram import make_linkedin_cover, make_teaching_diagram
from .gemini_images import generate_lesson_visuals
from .visual_plan import extract_visual_plan, remove_visual_plan
from .media_inserter import (
    inject_inline_visuals,
    validate_inserted_visuals,
)
from .github_client import GitHubPublisher
from .lesson_writer import LessonWriter
from .linkedin_client import LinkedInPublisher
from .linkedin_preflight import build_linkedin_package, preflight_linkedin_package
from .media_curator import append_media_resources, append_generated_teaching_visual, curate_open_media, media_credits_markdown, media_review_context
from .progress import load_progress, save_progress
from .publication_gate import final_publication_gate
from .quality import (
    combined_quality_report,
    deterministic_quality_checks,
    extract_json_object,
    failed_ai_review,
    normalize_ai_review,
    premium_review_passes,
    quality_failure_summary,
    weak_dimensions,
)
from .runtime import monitor
from .validator import extract_python, validate_lesson


RUN_LOCK = threading.Lock()

STEPS = [
    ('plan', 'Plan Lesson'),
    ('generate', 'Teach with OpenAI'),
    ('validate', 'Validate Lesson'),
    ('repair', 'Repair if Needed'),
    ('editorial', 'Premium Editorial Gate'),
    ('media', 'Curate Legal Media'),
    ('visual', 'Build Premium Visuals'),
    ('package', 'Build Article Package'),
    ('preflight', 'LinkedIn Preflight'),
    ('final_gate', 'Final Publication Gate'),
    ('github', 'Publish to GitHub'),
    ('linkedin', 'Publish to LinkedIn'),
    ('progress', 'Update Course Memory'),
]


def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


class PublicationBlockedError(RuntimeError):
    def __init__(self, message, attempts=0):
        RuntimeError.__init__(self, message)
        self.attempts = int(attempts or 0)


class RoboticsTeacherAgent(object):
    def __init__(self, curriculum_path='curriculum.json'):
        path = Path(curriculum_path)
        if not path.exists():
            raise RuntimeError('Curriculum file not found: {0}'.format(path))
        self.curriculum = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(self.curriculum, list) or not self.curriculum:
            raise RuntimeError('curriculum.json must contain a non-empty lesson list.')
        self.writer = LessonWriter()

    def _lesson_slug(self, lesson):
        return '{0:03d}-{1}'.format(lesson['class_no'], slugify(lesson['title']))

    def _lesson_preview_ready(self, lesson):
        slug = self._lesson_slug(lesson)
        lesson_path = Path('preview') / slug / 'README.md'
        return lesson_path.exists()

    def next_lesson(self):
        progress = load_progress()
        if not settings.auto_publish:
            generated_until = int(progress.get('last_generated_class', 0) or 0)
            for index, lesson in enumerate(self.curriculum[:generated_until]):
                if not self._lesson_preview_ready(lesson):
                    monitor.event(
                        'warning',
                        'Detected a missing local lesson package for Class {0}. Regenerating it before moving ahead.'.format(
                            lesson['class_no']))
                    return index, lesson
            completed = generated_until
        else:
            completed = int(progress.get('last_published_class', 0) or 0)
        index = completed
        if index >= len(self.curriculum):
            raise RuntimeError('Curriculum completed. Add the next curriculum module.')
        return index, self.curriculum[index]

    def _review(self, markdown, lesson, visual_context=None):
        static_report = deterministic_quality_checks(markdown)
        ai_review = None
        raw_review = None
        try:
            raw_review = (self.writer.review_premium_quality(markdown, lesson) if visual_context is None else self.writer.review_premium_quality(markdown, lesson, visual_context=visual_context))
        except Exception as exc:
            if settings.require_ai_quality_review:
                ai_review = failed_ai_review(
                    'AI editorial review request failed: {0}'.format(exc))
                monitor.event('error', ai_review['blocking_issues'][0])
            else:
                monitor.event(
                    'warning',
                    'AI quality review unavailable; static quality gate only: {0}'.format(exc))
            return static_report, ai_review

        try:
            ai_review = normalize_ai_review(extract_json_object(raw_review))
            return static_report, ai_review
        except Exception as parse_exc:
            last_error = parse_exc
            monitor.event(
                'warning',
                'Editorial review JSON was malformed; requesting automatic structured repair: {0}'.format(
                    parse_exc))

        repaired_text = raw_review
        for repair_attempt in range(1, 3):
            try:
                repaired_text = self.writer.repair_premium_review_json(
                    repaired_text, lesson, last_error)
                ai_review = normalize_ai_review(extract_json_object(repaired_text))
                monitor.event(
                    'success',
                    'Editorial review JSON repaired successfully on attempt {0}.'.format(
                        repair_attempt))
                return static_report, ai_review
            except Exception as exc:
                last_error = exc
                monitor.event(
                    'warning',
                    'Editorial JSON repair attempt {0} failed: {1}'.format(
                        repair_attempt, exc))

        if settings.require_ai_quality_review:
            ai_review = failed_ai_review(
                'AI editorial review remained malformed after automatic repair: {0}'.format(
                    last_error))
            monitor.event('error', ai_review['blocking_issues'][0])
        else:
            monitor.event(
                'warning',
                'AI editorial review could not be parsed after repair; static quality gate only.')
        return static_report, ai_review

    def _repair_until_valid(self, markdown, errors, context_label, max_attempts=3):
        """Repair generated lesson code/structure until it validates or attempts are exhausted."""
        current_errors = list(errors or [])
        attempts_used = 0

        if not current_errors:
            return markdown, current_errors, attempts_used

        for repair_round in range(1, max_attempts + 1):
            attempts_used = repair_round
            monitor.event(
                'warning',
                '{0} executable repair round {1}/{2}: {3}'.format(
                    context_label,
                    repair_round,
                    max_attempts,
                    ' | '.join(current_errors)[:1600]
                )
            )

            markdown = self.writer.repair_code(
                markdown,
                '\n'.join(current_errors)
            )

            current_errors = validate_lesson(markdown)

            if not current_errors:
                monitor.event(
                    'success',
                    '{0} executable validation repaired on round {1}.'.format(
                        context_label,
                        repair_round
                    )
                )
                break

        return markdown, current_errors, attempts_used

    def _premium_editorial_gate(self, markdown, lesson, output_dir):
        last_report = None
        polish_rounds = 0
        technical_rounds = 0
        review_round = 0
        max_reviews = 1 + settings.premium_quality_rewrite_rounds + settings.technical_quality_repair_rounds
        while review_round < max_reviews:
            static_report, ai_review = self._review(markdown, lesson)
            last_report = combined_quality_report(static_report, ai_review, polish_rounds + technical_rounds)
            monitor.quality(last_report)
            if premium_review_passes(static_report, ai_review):
                return markdown, ai_review, last_report

            blocking = (ai_review or {}).get('blocking_issues') or []
            dimensions = (ai_review or {}).get('dimensions') or {}
            technical_weak = (
                int(dimensions.get('technical_accuracy', 100)) < settings.premium_quality_min_dimension or
                int(dimensions.get('code_alignment', 100)) < settings.premium_quality_min_dimension or
                int(dimensions.get('consistency', 100)) < settings.premium_quality_min_dimension)

            if (blocking or technical_weak) and technical_rounds < settings.technical_quality_repair_rounds:
                technical_rounds += 1
                reason_text = ' | '.join(blocking or quality_failure_summary(last_report))[:2200]
                monitor.event(
                    'warning',
                    'Technical correction round {0}: {1}'.format(technical_rounds, reason_text))
                markdown = self.writer.repair_technical_quality(
                    markdown, json.dumps(ai_review or {}, indent=2), visual_context=None)
            elif polish_rounds < settings.premium_quality_rewrite_rounds:
                polish_rounds += 1
                reasons = quality_failure_summary(last_report)
                monitor.event('warning', 'Premium editorial polish round {0}: {1}'.format(
                    polish_rounds, ' | '.join(reasons)[:1600]))
                markdown = self.writer.polish_premium_quality(
                    markdown, json.dumps(ai_review or {}, indent=2), static_report.get('errors') or [])
            else:
                break

            errors = validate_lesson(markdown)
            if errors:
                monitor.event(
                    'warning',
                    'Correction changed executable content; running resilient code/structure repair: {0}'.format(
                        ' | '.join(errors)[:1200]
                    )
                )
                markdown, errors, code_repair_attempts = self._repair_until_valid(
                    markdown,
                    errors,
                    'Editorial-stage',
                    max_attempts=3
                )
                if errors:
                    raise PublicationBlockedError(
                        'Corrected lesson still fails executable validation after 3 repair rounds: ' +
                        ' | '.join(errors),
                        attempts=technical_rounds + polish_rounds + code_repair_attempts
                    )
            review_round += 1

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        (Path(output_dir) / 'FAILED_DRAFT.md').write_text(markdown, encoding='utf-8')
        (Path(output_dir) / 'QUALITY_REPORT.json').write_text(
            json.dumps(last_report or {}, indent=2), encoding='utf-8')
        raise PublicationBlockedError(
            'Premium quality gate remains blocked after automatic correction: ' +
            ' | '.join(quality_failure_summary(last_report or {})),
            attempts=technical_rounds + polish_rounds)

    def _post_media_editorial_gate(self, markdown, lesson, output_dir, visual_context, prior_rounds=0):
        last_report = None
        visual_rounds = 0
        technical_rounds = 0
        review_round = 0
        max_reviews = 1 + settings.post_media_repair_rounds + settings.technical_quality_repair_rounds
        while review_round < max_reviews:
            final_static, final_ai = self._review(markdown, lesson, visual_context=visual_context)
            last_report = combined_quality_report(
                final_static, final_ai, prior_rounds + visual_rounds + technical_rounds)
            monitor.quality(last_report)
            if premium_review_passes(final_static, final_ai):
                if visual_rounds or technical_rounds:
                    monitor.event(
                        'success',
                        'Final editorial remediation passed after {0} technical and {1} visual/editorial repair round(s).'.format(
                            technical_rounds, visual_rounds))
                return markdown, final_ai, last_report

            weak = weak_dimensions(final_ai)
            blocking = (final_ai or {}).get('blocking_issues') or []
            dimensions = (final_ai or {}).get('dimensions') or {}
            technical_weak = (
                int(dimensions.get('technical_accuracy', 100)) < settings.premium_quality_min_dimension or
                int(dimensions.get('code_alignment', 100)) < settings.premium_quality_min_dimension or
                int(dimensions.get('consistency', 100)) < settings.premium_quality_min_dimension)

            if (blocking or technical_weak) and technical_rounds < settings.technical_quality_repair_rounds:
                technical_rounds += 1
                reason_text = ' | '.join(blocking or quality_failure_summary(last_report))[:2400]
                monitor.event(
                    'warning',
                    'Post-media technical correction {0}: {1}'.format(technical_rounds, reason_text))
                markdown = self.writer.repair_technical_quality(
                    markdown, json.dumps(final_ai or {}, indent=2), visual_context=visual_context)
            elif visual_rounds < settings.post_media_repair_rounds:
                visual_rounds += 1
                weak_text = ', '.join(
                    '{0}={1}'.format(item['name'], item['score']) for item in weak) or 'general editorial quality'
                monitor.event(
                    'warning',
                    'Post-media quality remediation {0}: {1}.'.format(visual_rounds, weak_text))
                markdown = self.writer.polish_post_media_quality(
                    markdown, json.dumps(final_ai or {}, indent=2), visual_context)
            else:
                break

            # Every technical/editorial correction invalidates the previous executable-code verdict.
            # Re-run all deterministic and Python execution checks before asking the board again.
            errors = validate_lesson(markdown)
            if errors:
                monitor.event(
                    'warning',
                    'Remediation changed executable content; running resilient validator repair before re-review: {0}'.format(
                        ' | '.join(errors)[:1400]
                    )
                )
                markdown, errors, code_repair_attempts = self._repair_until_valid(
                    markdown,
                    errors,
                    'Post-media',
                    max_attempts=3
                )
                if errors:
                    raise PublicationBlockedError(
                        'Post-media correction still fails executable validation after 3 repair rounds: ' +
                        ' | '.join(errors),
                        attempts=technical_rounds + visual_rounds + code_repair_attempts
                    )
            review_round += 1

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        (Path(output_dir) / 'FAILED_FINAL.md').write_text(markdown, encoding='utf-8')
        (Path(output_dir) / 'QUALITY_REPORT.json').write_text(
            json.dumps(last_report or {}, indent=2), encoding='utf-8')
        raise PublicationBlockedError(
            'Final publication quality remains blocked after automatic technical/editorial remediation: ' +
            ' | '.join(quality_failure_summary(last_report or {})),
            attempts=technical_rounds + visual_rounds)

    def _write_code_labs(self, markdown, output_dir):
        code_dir = Path(output_dir) / 'code'
        code_dir.mkdir(parents=True, exist_ok=True)
        code_paths = []
        for index, code in enumerate(extract_python(markdown), 1):
            code_path = code_dir / 'lab_{0:02d}.py'.format(index)
            code_path.write_text(code + '\n', encoding='utf-8')
            code_paths.append(code_path)
            monitor.artifact('code', code_path, 'Validated Python lab {0}'.format(index))
        return code_paths

    def _lesson_url(self, slug):
        repo_dir = 'lessons/' + slug
        if settings.public_lesson_base_url:
            return '{0}/lessons/{1}/'.format(settings.public_lesson_base_url.rstrip('/'), slug)
        if settings.github_owner and settings.github_repo:
            return 'https://github.com/{0}/{1}/blob/{2}/{3}/README.md'.format(
                settings.github_owner, settings.github_repo, settings.github_branch, repo_dir)
        return 'http://127.0.0.1:{0}/lessons/{1}/'.format(settings.dashboard_port, slug)

    def _upload_lesson_package(self, github, output_dir, slug, class_no):
        repo_dir = 'lessons/' + slug
        allowed_suffixes = set(['.md', '.html', '.json', '.py', '.png', '.jpg', '.jpeg'])
        paths = []
        for path in Path(output_dir).rglob('*'):
            if path.is_file() and path.suffix.lower() in allowed_suffixes:
                paths.append(path)
        for path in sorted(paths):
            rel = str(path.relative_to(output_dir)).replace('\\', '/')
            github.put_bytes(
                repo_dir + '/' + rel,
                path.read_bytes(),
                'Professor OS Class {0}: update {1}'.format(class_no, rel))

    def run_once(self):
        if not RUN_LOCK.acquire(False):
            monitor.event('warning', 'Run request ignored because another lesson is already running.')
            raise RuntimeError('The teacher agent is already running.')

        step_id = 'plan'
        try:
            index, lesson = self.next_lesson()
            previous_title = self.curriculum[index - 1]['title'] if index > 0 else None
            next_title = self.curriculum[index + 1]['title'] if index + 1 < len(self.curriculum) else None
            class_no = lesson['class_no']
            slug = self._lesson_slug(lesson)
            out = Path('preview') / slug
            out.mkdir(parents=True, exist_ok=True)

            run_id = uuid.uuid4().hex[:10]
            mode = 'publish' if settings.auto_publish else 'preview'
            monitor.reset_run(run_id, class_no, lesson['title'], len(self.curriculum), mode, STEPS)

            monitor.step('plan', 'Reading curriculum position, prerequisites, and next-class objective.')
            monitor.event('info', 'Previous class: {0}'.format(previous_title or 'Course beginning'))
            monitor.event('info', 'Next class: {0}'.format(next_title or 'Curriculum complete'))
            monitor.complete_step('plan', 'Lesson plan context is ready.')

            step_id = 'generate'
            monitor.step('generate', 'OpenAI is drafting the full classroom lesson, examples, and Python activities.')
            markdown = self.writer.write(lesson, previous_title, next_title)
            monitor.complete_step('generate', 'First lesson draft generated.')

            step_id = 'validate'
            monitor.step('validate', 'Checking required chapters and executing safe Python code blocks.')
            errors = validate_lesson(markdown)
            monitor.complete_step('validate', 'Validation found {0} issue(s).'.format(len(errors)))

            step_id = 'repair'
            if errors:
                monitor.step('repair', 'Repairing {0} structural/code validation issue(s).'.format(len(errors)))
                markdown, errors, repair_attempts = self._repair_until_valid(
                    markdown,
                    errors,
                    'Initial-validation',
                    max_attempts=3
                )
                if errors:
                    monitor.fail_step(
                        'repair',
                        'Lesson still failed validation after {0} repair rounds: {1}'.format(
                            repair_attempts,
                            ' | '.join(errors)
                        )
                    )
                    raise RuntimeError(
                        'Lesson failed validation after {0} repair rounds: {1}'.format(
                            repair_attempts,
                            '\n'.join(errors)
                        )
                    )
                monitor.complete_step(
                    'repair',
                    'All validation issues repaired successfully after {0} round(s).'.format(
                        repair_attempts
                    )
                )
            else:
                monitor.complete_step('repair', 'No structural/code repair required.')

            step_id = 'editorial'
            monitor.step('editorial', 'Running the expert editorial board across pedagogy, accuracy, depth, clarity, originality, and accessibility.')
            markdown, ai_review, quality_report = self._premium_editorial_gate(markdown, lesson, out)
            monitor.complete_step('editorial', 'Premium editorial gate passed at {0}/100.'.format(
                (ai_review or {}).get('overall_score', 'static-only')))

            step_id = 'media'
            monitor.step('media', 'Checking whether a verified open-license visual/video resource would materially improve understanding.')
            media_result = curate_open_media(lesson, ai_review, out)
            markdown = append_media_resources(markdown, media_result)
            credits_path = out / 'MEDIA_CREDITS.md'
            credits_path.write_text(media_credits_markdown(media_result), encoding='utf-8')
            monitor.artifact('media', credits_path, 'Media license and attribution record')
            if media_result.get('used'):
                monitor.complete_step('media', 'Open media enrichment added with machine-readable license provenance.')
            else:
                monitor.complete_step('media', 'No external media needed; Professor OS visuals remain primary.')

            # Render the actual visual assets BEFORE the final visual-teaching review.
            # The previous implementation reviewed visual_teaching_plan before these assets existed.
            step_id = 'visual'
            monitor.step(
                'visual',
                'Building the lesson visual plan and generating premium Gemini teaching assets.'
            )

            visual_plan = extract_visual_plan(markdown)

            visual_plan_path = out / 'VISUAL_PLAN.json'
            visual_plan_path.write_text(
                json.dumps(visual_plan, indent=2),
                encoding='utf-8'
            )

            monitor.artifact(
                'visual',
                visual_plan_path,
                'Machine-readable Gemini visual production plan'
            )

            visual_assets = generate_lesson_visuals(
                visual_plan,
                out
            )

            hero_path = Path(visual_assets['hero']['path'])
            inline_assets = visual_assets['inline']

            for asset in inline_assets:
                monitor.artifact(
                    'visual',
                    Path(asset['path']),
                    'Gemini teaching visual for {0}'.format(
                        asset['section_heading']
                    )
                )

            monitor.artifact(
                'visual',
                hero_path,
                'Premium Gemini lesson hero'
            )

            diagram_path = out / 'diagram.png'

            make_teaching_diagram(
                class_no,
                lesson['title'],
                lesson.get('concepts', ''),
                diagram_path
            )

            monitor.artifact(
                'visual',
                diagram_path,
                'Professor OS engineering teaching schematic'
            )

            # Insert every planned Gemini teaching visual beside the lesson section
            # it was created to explain.
            markdown = inject_inline_visuals(
                markdown,
                inline_assets
            )

            # Keep the existing Professor OS engineering schematic visible too.
            markdown = append_generated_teaching_visual(
                markdown,
                lesson
            )

            # The Visual Generation Plan is machine metadata only.
            # Keep VISUAL_PLAN.json, but remove the plan from the student-facing lesson.
            markdown = remove_visual_plan(markdown)

            # Fail closed if a planned inline visual is missing, invalid, or not inserted.
            visual_errors = validate_inserted_visuals(
                markdown,
                inline_assets,
                out
            )

            if visual_errors:
                raise PublicationBlockedError(
                    'Premium visual package failed validation: '
                    + ' | '.join(visual_errors)
                )

            monitor.complete_step(
                'visual',
                'Generated and inserted {0} premium Gemini lesson visuals.'.format(
                    visual_assets['count']
                )
            )

            # Tell the final editorial board exactly which generated visuals exist
            # and where they were inserted.
            visual_context = media_review_context(
                media_result,
                hero_path=hero_path,
                diagram_path=diagram_path
            )

            inline_context = []
            for asset in inline_assets:
                inline_context.append(
                    (
                        'Gemini inline teaching visual: {filename}; '
                        'inserted after {section}; '
                        'type={visual_type}; '
                        'caption={caption}; '
                        'alt={alt}.'
                    ).format(
                        filename=asset.get('filename', ''),
                        section=asset.get('section_heading', ''),
                        visual_type=asset.get('visual_type', ''),
                        caption=asset.get('caption', ''),
                        alt=asset.get('alt_text', ''),
                    )
                )

            if inline_context:
                visual_context += '\n' + '\n'.join(inline_context)

            # Review the exact post-media + generated-visual lesson and automatically repair weak dimensions.
            step_id = 'editorial'
            monitor.step(
                'editorial',
                'Re-reviewing the exact final lesson after media and generated visuals, with targeted remediation if needed.'
            )
            markdown, final_ai, final_quality_report = self._post_media_editorial_gate(
                markdown,
                lesson,
                out,
                visual_context,
                quality_report.get('rewrite_rounds_used', 0)
            )

            # The final editorial repair pass is allowed to rewrite Markdown, so verify
            # once more that it did not accidentally remove a required Gemini visual.
            visual_errors = validate_inserted_visuals(
                markdown,
                inline_assets,
                out
            )
            if visual_errors:
                raise PublicationBlockedError(
                    'Final editorial pass damaged the premium visual package: '
                    + ' | '.join(visual_errors)
                )

            monitor.complete_step(
                'editorial',
                'Final post-media editorial gate passed at {0}/100.'.format(
                    (final_ai or {}).get('overall_score', 'static-only')
                )
            )

            step_id = 'package'
            monitor.step('package', 'Building the final lesson, web article, labs, quality report, and attribution record.')
            lesson_path = out / 'README.md'
            lesson_path.write_text(markdown, encoding='utf-8')
            monitor.artifact('lesson', lesson_path, 'Final lesson Markdown')
            code_paths = self._write_code_labs(markdown, out)
            quality_path = out / 'QUALITY_REPORT.json'
            quality_path.write_text(json.dumps(final_quality_report, indent=2), encoding='utf-8')
            monitor.artifact('quality', quality_path, 'Premium editorial quality report')
            article_path = out / 'index.html'
            previous_lesson = self.curriculum[index - 1] if index > 0 else None
            next_lesson = self.curriculum[index + 1] if index + 1 < len(self.curriculum) else None
            previous_slug = self._lesson_slug(previous_lesson) if previous_lesson else None
            next_slug = self._lesson_slug(next_lesson) if next_lesson else None
            navigation = {
                'previous': ({
                    'class_no': previous_lesson['class_no'],
                    'title': previous_lesson['title'],
                    'url': ('/lessons/{0}/'.format(previous_slug)
                            if (Path('preview') / previous_slug / 'index.html').exists() else None),
                } if previous_lesson else None),
                'next': ({
                    'class_no': next_lesson['class_no'],
                    'title': next_lesson['title'],
                    'url': ('/lessons/{0}/'.format(next_slug)
                            if (Path('preview') / next_slug / 'index.html').exists() else None),
                } if next_lesson else None),
            }
            render_premium_article(
                markdown, lesson, article_path, hero_filename='hero.png',
                quality_report=final_quality_report, navigation=navigation)
            # Keep article.html as a convenient explicit local filename while index.html is the canonical web entry point.
            article_alias = out / 'article.html'
            article_alias.write_text(article_path.read_text(encoding='utf-8'), encoding='utf-8')
            monitor.artifact('article', article_path, 'Responsive premium lesson article')

            lesson_url = self._lesson_url(slug)
            linkedin_package = build_linkedin_package(lesson, final_ai, lesson_url)
            package_path = out / 'linkedin_package.json'
            package_path.write_text(json.dumps(linkedin_package, indent=2), encoding='utf-8')
            preview_path = out / 'linkedin_preview.html'
            render_linkedin_preview(linkedin_package, preview_path, hero_filename='hero.png')
            monitor.artifact('linkedin', preview_path, 'LinkedIn article-card preflight preview')
            monitor.complete_step('package', 'Publication package created at {0}.'.format(out))

            step_id = 'preflight'
            monitor.step('preflight', 'Double-checking LinkedIn copy length, typography, spacing, hashtags, source URL, alt text, and image dimensions.')
            preflight = preflight_linkedin_package(linkedin_package, hero_path)
            preflight_path = out / 'LINKEDIN_PREFLIGHT.json'
            preflight_path.write_text(json.dumps(preflight, indent=2), encoding='utf-8')
            monitor.linkedin_preflight(preflight)
            if not preflight.get('passed'):
                raise RuntimeError('LinkedIn preflight blocked publishing: ' + ' | '.join(preflight.get('errors') or []))
            monitor.complete_step('preflight', 'LinkedIn display preflight passed. Article card is publication-ready.')

            step_id = 'final_gate'
            monitor.step('final_gate', 'Auditing final content, code package, rendered article, visuals, media licensing, and LinkedIn preview before any upload.')
            publication_gate = final_publication_gate(
                lesson, out, final_quality_report, preflight, media_result, code_paths)
            monitor.artifact('quality', out / 'PUBLICATION_GATE.json', 'Final publication gate report')
            if not publication_gate.get('passed'):
                raise RuntimeError('Final publication gate blocked publishing: ' + ' | '.join(publication_gate.get('errors') or []))
            monitor.complete_step('final_gate', 'Every publication-quality gate passed. Upload is now permitted.')

            linkedin_result = None
            if settings.auto_publish:
                step_id = 'github'
                monitor.step('github', 'Uploading the validated lesson package to GitHub before LinkedIn publishing.')
                github = GitHubPublisher()
                self._upload_lesson_package(github, out, slug, class_no)
                monitor.integration('github', True, 'Validated lesson package uploaded successfully.')
                monitor.complete_step('github', 'Validated lesson package uploaded successfully.')

                step_id = 'linkedin'
                if settings.linkedin_access_token and settings.linkedin_author_urn:
                    monitor.step('linkedin', 'Uploading the validated thumbnail and publishing the preflighted article card to LinkedIn.')
                    linkedin_result = LinkedInPublisher().publish_lesson_post(
                        linkedin_package, hero_path=hero_path)
                    monitor.integration('linkedin', True, 'Article post published successfully.')
                    monitor.complete_step('linkedin', 'LinkedIn article post published successfully.')
                else:
                    monitor.complete_step('linkedin', 'LinkedIn skipped because credentials are not configured.')
            else:
                monitor.complete_step('github', 'Preview mode: lesson GitHub publishing skipped.')
                monitor.complete_step('linkedin', 'Preview mode: LinkedIn publishing skipped.')

            step_id = 'progress'
            monitor.step('progress', 'Saving curriculum memory so the next run knows where to continue.')
            save_progress(class_no, published=settings.auto_publish)
            monitor.complete_step('progress', 'Course memory updated to Class {0}.'.format(class_no))
            message = 'Class {0} completed in {1} mode with premium quality gates passed.'.format(class_no, mode)
            monitor.finish(message)
            return {
                'mode': mode,
                'class_no': class_no,
                'path': str(out),
                'lesson_url': lesson_url,
                'quality': final_quality_report,
                'preflight': preflight,
                'publication_gate': publication_gate,
                'linkedin': linkedin_result,
            }
        except PublicationBlockedError as exc:
            message = str(exc)

            # Persist the exact failed lesson and a compact machine-readable diagnostic.
            # GitHub Actions can upload these even when --once exits with code 2.
            try:
                failed_out = locals().get('out')
                failed_markdown = locals().get('markdown')
                if failed_out:
                    failed_out = Path(failed_out)
                    failed_out.mkdir(parents=True, exist_ok=True)
                    if failed_markdown:
                        (failed_out / 'FAILED_RUN.md').write_text(
                            failed_markdown,
                            encoding='utf-8'
                        )
                    (failed_out / 'FAILED_RUN.json').write_text(
                        json.dumps({
                            'class_no': locals().get('class_no'),
                            'step': step_id,
                            'reason': message,
                            'attempts': getattr(exc, 'attempts', 0),
                        }, indent=2),
                        encoding='utf-8'
                    )
            except Exception as diagnostic_exc:
                monitor.event(
                    'warning',
                    'Could not persist blocked-run diagnostics: {0}'.format(diagnostic_exc)
                )

            try:
                monitor.fail_step(step_id, 'Publication hold: ' + message)
            except Exception:
                pass
            monitor.hold(message, attempts=getattr(exc, 'attempts', 0))
            return {
                'mode': 'blocked',
                'class_no': locals().get('class_no'),
                'path': str(locals().get('out', '')),
                'publication_blocked': True,
                'reason': message,
            }
        except Exception as exc:
            message = '{0}: {1}'.format(type(exc).__name__, exc)
            try:
                if step_id in ('github', 'linkedin'):
                    monitor.integration(step_id, False, message)
                monitor.fail_step(step_id, message)
            except Exception:
                pass
            monitor.fail(message)
            raise
        finally:
            RUN_LOCK.release()
