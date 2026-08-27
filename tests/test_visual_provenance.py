import pytest

from teacher_agent.visual_plan import extract_visual_plan


def _lesson_with_plan(source='gemini', visual_type='diagram', prompt='Explain sensing'):
    return '''# Class 1: What Is a Robot?
## Next Class
Next.

## Visual Generation Plan
```json
{{
  "hero_image": {{
    "needed": true,
    "section": "top",
    "visual_type": "premium robotics hero illustration",
    "source": "gemini",
    "prompt": "Premium RoboRover hero",
    "caption": "Hero caption",
    "alt_text": "Hero alt"
  }},
  "inline_visuals": [
    {{
      "section_heading": "## The Big Idea",
      "visual_type": "{visual_type}",
      "source": "{source}",
      "prompt": "{prompt}",
      "caption": "Concept caption",
      "alt_text": "Concept alt"
    }},
    {{
      "section_heading": "## Worked Robotics Example",
      "visual_type": "diagram",
      "source": "gemini",
      "prompt": "Worked example diagram",
      "caption": "Worked example caption",
      "alt_text": "Worked example alt"
    }}
  ]
}}
```
'''.format(source=source, visual_type=visual_type, prompt=prompt)


def test_visual_plan_accepts_gemini_only_assets():
    plan = extract_visual_plan(_lesson_with_plan())
    assert plan['hero_image']['source'] == 'gemini'
    assert all(item['source'] == 'gemini' for item in plan['inline_visuals'])


def test_visual_plan_rejects_explicit_external_asset():
    with pytest.raises(RuntimeError):
        extract_visual_plan(
            _lesson_with_plan(
                source='external',
                visual_type='independently sourced photograph',
                prompt='Find a licensed photograph from Wikimedia'
            )
        )


def test_visual_plan_normalizes_missing_source_to_gemini():
    markdown = _lesson_with_plan().replace('      "source": "gemini",\n', '', 1)
    plan = extract_visual_plan(markdown)
    assert plan['inline_visuals'][0]['source'] == 'gemini'
