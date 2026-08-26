import json
import re

def extract_visual_plan(markdown):
    match = re.search(
        r'## Visual Generation Plan\s*```json\s*(\{.*?\})\s*```',
        markdown,
        re.S
    )
    if not match:
        raise RuntimeError('Missing Visual Generation Plan JSON block.')
    return json.loads(match.group(1))
