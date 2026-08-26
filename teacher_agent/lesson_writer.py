from .config import settings
from .http_utils import request_with_retry
from .prompts import (
    SYSTEM_PROMPT,
    lesson_prompt,
    premium_review_prompt,
    post_media_polish_prompt,
    premium_polish_prompt,
    technical_correction_prompt,
)
from .runtime import monitor
from .quality import PREMIUM_REVIEW_SCHEMA


class LessonWriter(object):
    def __init__(self):
        if not settings.openai_api_key:
            raise RuntimeError('OPENAI_API_KEY is missing from .env')
        self.url = 'https://api.openai.com/v1/responses'
        self.headers = {
            'Authorization': 'Bearer ' + settings.openai_api_key,
            'Content-Type': 'application/json',
        }

    def _call_openai(self, instructions, user_input, text_format=None):
        payload = {
            'model': settings.openai_model,
            'instructions': instructions,
            'input': user_input,
        }
        if text_format is not None:
            payload['text'] = {'format': text_format}

        response = request_with_retry(
            'POST',
            self.url,
            headers=self.headers,
            json=payload,
            timeout=settings.openai_timeout,
            max_attempts=settings.api_max_attempts,
            base_delay=settings.api_retry_base_delay,
        )
        try:
            response.raise_for_status()
        except Exception:
            body = response.text[-2000:] if response.text else '(empty response body)'
            raise RuntimeError(
                'OpenAI API returned HTTP {0}: {1}'.format(
                    response.status_code,
                    body
                )
            )

        try:
            data = response.json()
        except ValueError:
            raise RuntimeError('OpenAI returned a non-JSON response.')

        texts = []
        for item in data.get('output', []):
            for content in item.get('content', []):
                if content.get('type') == 'output_text':
                    text = content.get('text', '')
                    if text:
                        texts.append(text)

        if not texts:
            raise RuntimeError(
                'OpenAI returned no output_text. Response keys: {0}'.format(
                    ', '.join(sorted(data.keys()))
                )
            )

        joined = '\n'.join(texts)
        monitor.event(
            'success',
            'OpenAI returned {0:,} characters of lesson content.'.format(len(joined))
        )
        return joined

    def write(self, lesson, previous_title=None, next_title=None):
        instructions = SYSTEM_PROMPT.format(
            class_no=lesson['class_no'],
            title=lesson['title']
        )
        return self._call_openai(
            instructions,
            lesson_prompt(lesson, previous_title, next_title),
        )

    def repair_code(self, lesson_markdown, error_report):
        instructions = (
            'You are repairing executable Python examples inside a robotics teaching lesson. '
            'Return the COMPLETE corrected Markdown lesson only. '
            'Preserve all required headings, explanations, diagrams, media references, and teaching continuity. '
            'Change only what is necessary to correct validation errors. '

            'CRITICAL VALIDATION RULE: every fenced ```python code block is executed '
            'IN ISOLATION in a fresh Python process. Therefore EVERY Python code block '
            'must be independently executable. A block may NOT depend on variables, '
            'functions, classes, imports, constants, or setup defined in another code block. '

            'If a demonstration needs find_safe_route(), start, goal, a class, an import, '
            'or any other dependency, define or import that dependency inside that same '
            'Python block. '

            'Do not solve validation failures by deleting meaningful teaching examples. '
            'Make examples self-contained instead. '

            'If the lesson contains a ## Visual Generation Plan section, preserve the ENTIRE '
            'heading and its fenced ```json block exactly as machine-readable metadata. '
            'Keep that JSON syntactically valid and keep it after ## Next Class. '

            'If the lesson already contains local image references such as inline_01.png, '
            'inline_02.png, or diagram.png, preserve those image references, their captions, '
            'and their surrounding teaching context. '

            'All executable code must run on Python 3.7. '
            'Do not use syntax introduced after Python 3.7. '
            'Before returning the lesson, mentally execute every Python block independently.'
        )

        user_input = (
            'LESSON:\n{0}\n\n'
            'VALIDATION ERRORS:\n{1}'
        ).format(lesson_markdown, error_report)

        return self._call_openai(
            instructions,
            user_input
        )

    def _premium_review_format(self):
        return {
            'type': 'json_schema',
            'name': 'premium_editorial_review',
            'description': 'Strict editorial review for a Professor OS robotics lesson.',
            'strict': True,
            'schema': PREMIUM_REVIEW_SCHEMA,
        }

    def review_premium_quality(self, lesson_markdown, lesson, visual_context=None):
        instructions = (
            'You are a strict senior editorial board for robotics education. '
            'Return only the requested structured review. Be conservative with scores.'
        )
        user_input = premium_review_prompt(
            lesson_markdown,
            lesson['class_no'],
            lesson['title'],
            visual_context=visual_context
        )
        try:
            return self._call_openai(
                instructions,
                user_input,
                text_format=self._premium_review_format()
            )
        except RuntimeError as exc:
            # Older/unsupported model configurations can reject strict JSON schema.
            # Fall back to JSON mode, which still forces syntactically valid JSON.
            message = str(exc).lower()
            if (
                'json_schema' not in message and
                'response format' not in message and
                'text.format' not in message and
                'unsupported' not in message
            ):
                raise
            monitor.event(
                'warning',
                'Strict editorial JSON schema was rejected; falling back to JSON-object mode.'
            )
            return self._call_openai(
                instructions,
                user_input,
                text_format={'type': 'json_object'}
            )

    def repair_premium_review_json(self, malformed_text, lesson, parse_error):
        instructions = (
            'You are repairing a malformed editorial-review response. '
            'Return only the corrected structured review. Do not review the lesson again unless needed '
            'to fill a required field. Preserve the original scores and meaning whenever possible.'
        )
        user_input = (
            'The previous review could not be parsed as JSON.\n'
            'Parse error: {0}\n\n'
            'Lesson: Class {1}: {2}\n\n'
            'MALFORMED REVIEW:\n{3}'
        ).format(
            parse_error,
            lesson['class_no'],
            lesson['title'],
            malformed_text[:12000]
        )
        try:
            return self._call_openai(
                instructions,
                user_input,
                text_format=self._premium_review_format()
            )
        except RuntimeError as exc:
            message = str(exc).lower()
            if (
                'json_schema' not in message and
                'response format' not in message and
                'text.format' not in message and
                'unsupported' not in message
            ):
                raise
            return self._call_openai(
                instructions,
                user_input,
                text_format={'type': 'json_object'}
            )

    def repair_technical_quality(self, lesson_markdown, review_json, visual_context=None):
        instructions = (
            'You are a senior robotics professor and software verification engineer. '
            'Correct every blocking factual, mathematical, simulation, and code-semantic issue. '
            'Return the complete corrected Markdown lesson only. Do not merely explain the fix.'
        )
        return self._call_openai(
            instructions,
            technical_correction_prompt(
                lesson_markdown,
                review_json,
                visual_context
            )
        )

    def polish_post_media_quality(self, lesson_markdown, review_json, visual_context):
        instructions = (
            'You are a senior robotics teacher and visual-learning editor. '
            'Return the complete improved Markdown lesson only. Preserve valid media and code.'
        )
        return self._call_openai(
            instructions,
            post_media_polish_prompt(
                lesson_markdown,
                review_json,
                visual_context
            )
        )

    def polish_premium_quality(self, lesson_markdown, review_json, static_errors):
        instructions = (
            'You are a senior robotics teacher, engineer, and technical editor. '
            'Return the complete improved Markdown lesson only. '
            'All code must remain Python 3.7 compatible.'
        )
        return self._call_openai(
            instructions,
            premium_polish_prompt(
                lesson_markdown,
                review_json,
                static_errors
            )
        )
