from html.parser import HTMLParser
from pathlib import Path


class StructureParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.stack = []
        self.parents = {}
        self.ids = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = set((attrs.get('class') or '').split())
        node = attrs.get('id') or (
            'hero-window' if 'hero-window' in classes else
            'side-stack' if 'side-stack' in classes else
            'home-grid' if 'home-grid' in classes else
            None
        )
        parent = self.stack[-1][1] if self.stack else None
        if node:
            self.parents[node] = parent
            self.ids[node] = self.ids.get(node, 0) + 1
        self.stack.append((tag, node or parent))

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break


def _home():
    return Path(
        'teacher_agent/templates/student_site.html'
    ).read_text(encoding='utf-8')


def test_home_grid_keeps_hero_and_sidebar_as_siblings():
    parser = StructureParser()
    parser.feed(_home())

    assert parser.parents.get('hero-window') == 'home-grid'
    assert parser.parents.get('side-stack') == 'home-grid'


def test_professor_render_has_no_leftover_previous_scene_markup():
    text = _home()

    assert text.count('id="professorCore"') == 1
    assert text.count('id="osCanvas"') == 1
    assert text.count('id="professorRenderStage"') == 1
    assert text.count('id="canvasState"') == 1

    assert 'scene-badge-stack' not in text
    assert 'Ambient parallax · live state pulse · knowledge orbit' not in text


def test_professor_render_has_layout_containment_and_responsive_guard():
    text = _home()

    assert 'contain:layout paint' in text
    assert '@media(max-width:1040px)' in text
    assert '.hero-canvas-wrap{min-height:390px}' in text
