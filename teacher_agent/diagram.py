from pathlib import Path
import math
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

from .config import settings
from .gemini_image_client import GeminiImageClient
from .runtime import monitor


BG = '#07111a'
PANEL = '#0b1722'
TEXT = '#eef9ff'
MUTED = '#91aebf'
CYAN = '#59e8ef'
BLUE = '#6f9cff'
AQUA = '#9afff9'
LINE = '#25465b'


def _clean_concepts(concepts):
    items = [item.strip() for item in (concepts or '').split(',') if item.strip()]
    return items[:5] or ['Sense', 'Think', 'Act']


def _gemini_enabled():
    # Unit tests must never spend Gemini credits or become nondeterministic
    # just because CI has GEMINI_API_KEY configured.
    if os.getenv('PYTEST_CURRENT_TEST'):
        return False

    return bool(settings.use_gemini_images and settings.gemini_api_key)


def _hero_prompt(class_no, title, concepts):
    concept_text = ', '.join(_clean_concepts(concepts))
    return (
        'Create a premium, realistic, highly relevant 16:9 hero image for a robotics lesson website. '
        'The lesson is "{0}" for Class {1:02d}. '
        'Key concepts: {2}. '
        'Show believable robotics hardware, sensors, motion, experimentation, or a lab/classroom environment that matches the topic. '
        'Style: professional, premium, realistic, cinematic, educational, polished, modern, dark navy and turquoise-blue palette, suitable for a high-end edtech website. '
        'Do not make it childish, cartoony, toy-like, or cluttered. '
        'Do not include watermarks. Keep text minimal or none. Leave clean composition with some breathing room.'
    ).format(title, class_no, concept_text)


def _diagram_prompt(class_no, title, concepts):
    concept_text = ', '.join(_clean_concepts(concepts))
    return (
        'Create a premium 16:9 educational visual for a robotics lesson website. '
        'Lesson title: "{0}" for Class {1:02d}. Concepts: {2}. '
        'Make it look like a polished teaching infographic or systems diagram that helps a student understand the flow of the idea. '
        'Use a professional dark navy and turquoise theme, clean layout, arrows, blocks, labels, and visual hierarchy. '
        'The image should feel like an expert robotics teacher prepared it for students. '
        'Keep the labels short, readable, and relevant. Avoid childish cartoon styling. Avoid unnecessary decoration.'
    ).format(title, class_no, concept_text)


def _try_gemini_image(prompt, output_path):
    if not _gemini_enabled():
        return False
    try:
        GeminiImageClient().generate_image(prompt, output_path)
        return True
    except Exception as exc:
        monitor.event(
            'warning',
            'Gemini image generation failed; falling back to local renderer: {0}'.format(exc)
        )
        return False


def _fallback_linkedin_cover(class_no, title, concepts, output_path, photo_path=None):
    concepts_list = _clean_concepts(concepts)
    fig = plt.figure(figsize=(12, 6.75), dpi=100, facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(BG)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    photo_used = False
    if photo_path:
        try:
            image = plt.imread(str(photo_path))
            ax.imshow(image, extent=[0, 1, 0, 1], aspect='auto', zorder=0)
            ax.add_patch(Rectangle((0, 0), 1, 1, facecolor='#02070c', alpha=0.58, zorder=1))
            ax.add_patch(Rectangle((0, 0), 0.58, 1, facecolor='#02070c', alpha=0.62, zorder=2))
            photo_used = True
        except Exception:
            photo_used = False

    for radius, alpha, color in [
        (0.28, 0.08, BLUE), (0.22, 0.10, CYAN), (0.16, 0.12, AQUA)
    ]:
        circle = Circle(
            (0.80, 0.50),
            radius,
            facecolor='none',
            edgecolor=color,
            linewidth=2.0,
            alpha=(alpha * 0.55 if photo_used else alpha),
            zorder=3
        )
        ax.add_patch(circle)

    xs = [0.58 + (index / 160.0) * 0.42 for index in range(161)]
    ys = []
    for index, x in enumerate(xs):
        phase = (x - 0.58) * 22.0
        envelope = 0.045 + 0.025 * math.sin((x - 0.58) * 8.0)
        ys.append(
            0.50
            + envelope * math.sin(phase)
            + 0.018 * math.sin(phase * 2.2)
        )

    ax.plot(
        xs,
        ys,
        color=CYAN,
        linewidth=1.8,
        alpha=(0.48 if photo_used else 0.75),
        zorder=3
    )
    ax.scatter(
        xs[::5],
        ys[::5],
        s=12,
        color=BLUE,
        alpha=(0.42 if photo_used else 0.65),
        zorder=3
    )

    ax.text(
        0.07,
        0.84,
        'PROFESSOR OS  /  ROBOTICS CLASS {0:02d}'.format(class_no),
        color=CYAN,
        fontsize=12,
        fontweight='bold'
    )
    ax.text(
        0.07,
        0.67,
        title,
        color=TEXT,
        fontsize=30,
        fontweight='bold',
        va='top',
        wrap=True
    )
    ax.text(
        0.07,
        0.43,
        'Build the intuition. Test the math. Run the code. Understand the robot.',
        color=MUTED,
        fontsize=13,
        wrap=True
    )

    y = 0.30
    x = 0.07
    for concept in concepts_list[:4]:
        width = min(0.18, 0.055 + 0.010 * len(concept))
        box = FancyBboxPatch(
            (x, y),
            width,
            0.055,
            boxstyle='round,pad=0.009,rounding_size=0.018',
            facecolor=PANEL,
            edgecolor=LINE,
            linewidth=1.0
        )
        ax.add_patch(box)
        ax.text(
            x + width / 2.0,
            y + 0.0275,
            concept.title(),
            ha='center',
            va='center',
            color=AQUA,
            fontsize=9.5,
            fontweight='bold'
        )
        x += width + 0.014
        if x > 0.50:
            break

    ax.text(0.07, 0.09, 'Built by Connect.Vin', color=MUTED, fontsize=10)

    fig.savefig(
        str(output_path),
        dpi=100,
        facecolor=BG,
        bbox_inches=None,
        pad_inches=0
    )
    plt.close(fig)
    return output_path


def _fallback_teaching_diagram(class_no, title, concepts, output_path):
    concepts_list = _clean_concepts(concepts)
    fig = plt.figure(figsize=(12, 6.75), dpi=120, facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(BG)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    for x in [0.05 + i * 0.045 for i in range(21)]:
        ax.plot([x, x], [0.12, 0.82], color=LINE, alpha=0.11, linewidth=0.55)

    for y in [0.12 + i * 0.045 for i in range(16)]:
        ax.plot([0.05, 0.95], [y, y], color=LINE, alpha=0.11, linewidth=0.55)

    ax.text(
        0.055,
        0.92,
        'PROFESSOR OS  /  ENGINEERING VIEW  /  CLASS {0:02d}'.format(class_no),
        fontsize=10.5,
        weight='bold',
        color=CYAN,
        family='sans-serif'
    )
    ax.text(
        0.055,
        0.845,
        title,
        fontsize=23,
        weight='bold',
        color=TEXT,
        wrap=True
    )
    ax.text(
        0.055,
        0.785,
        'A technical relationship map for today\'s core ideas',
        fontsize=11.5,
        color=MUTED
    )

    n = len(concepts_list)
    left = 0.075
    right = 0.925
    y = 0.47
    gap = 0.018
    total_gap = gap * max(0, n - 1)
    width = (right - left - total_gap) / float(max(1, n))

    for index, concept in enumerate(concepts_list):
        x = left + index * (width + gap)
        edge = CYAN if index == 0 else (BLUE if index == n - 1 else LINE)

        box = FancyBboxPatch(
            (x, y - 0.075),
            width,
            0.15,
            boxstyle='round,pad=0.008,rounding_size=0.012',
            facecolor=PANEL,
            edgecolor=edge,
            linewidth=1.35
        )
        ax.add_patch(box)

        ax.text(
            x + 0.018,
            y + 0.035,
            '0{0}'.format(index + 1),
            color=MUTED,
            fontsize=8.5,
            weight='bold',
            ha='left'
        )
        ax.text(
            x + width / 2.0,
            y - 0.008,
            concept.upper(),
            ha='center',
            va='center',
            fontsize=10.5,
            color=TEXT,
            weight='bold',
            wrap=True
        )

        if index < n - 1:
            x1 = x + width + 0.003
            x2 = x + width + gap - 0.003
            ax.annotate(
                '',
                xy=(x2, y),
                xytext=(x1, y),
                arrowprops=dict(
                    arrowstyle='-|>',
                    linewidth=1.4,
                    color=CYAN,
                    alpha=.75
                )
            )

    ax.text(
        0.075,
        0.66,
        'INPUT / OBSERVATION',
        color=MUTED,
        fontsize=9,
        weight='bold'
    )
    ax.plot(
        [0.075, 0.22],
        [0.64, 0.64],
        color=CYAN,
        linewidth=1.2,
        alpha=.55
    )

    ax.text(
        0.925,
        0.66,
        'OUTPUT / BEHAVIOR',
        color=MUTED,
        fontsize=9,
        weight='bold',
        ha='right'
    )
    ax.plot(
        [0.78, 0.925],
        [0.64, 0.64],
        color=BLUE,
        linewidth=1.2,
        alpha=.55
    )

    ax.text(
        0.075,
        0.245,
        'ENGINEERING CHECK',
        color=CYAN,
        fontsize=9,
        weight='bold'
    )
    ax.text(
        0.075,
        0.205,
        'What is measured?  →  What is computed?  →  What changes in the physical system?',
        fontsize=11,
        color=TEXT
    )
    ax.text(
        0.075,
        0.155,
        'Use the worked example and Python lab to test this relationship rather than memorize it.',
        fontsize=10.5,
        color=MUTED
    )
    ax.text(
        0.94,
        0.07,
        'Built by Connect.Vin',
        fontsize=9.5,
        color=MUTED,
        ha='right'
    )

    fig.savefig(
        str(output_path),
        dpi=120,
        facecolor=BG,
        bbox_inches=None,
        pad_inches=0
    )
    plt.close(fig)

    return output_path


def make_linkedin_cover(class_no, title, concepts, output_path, photo_path=None):
    output_path = Path(output_path)

    if _try_gemini_image(
        _hero_prompt(class_no, title, concepts),
        output_path
    ):
        return output_path

    return _fallback_linkedin_cover(
        class_no,
        title,
        concepts,
        output_path,
        photo_path=photo_path
    )


def make_teaching_diagram(class_no, title, concepts, output_path):
    output_path = Path(output_path)

    if _try_gemini_image(
        _diagram_prompt(class_no, title, concepts),
        output_path
    ):
        return output_path

    return _fallback_teaching_diagram(
        class_no,
        title,
        concepts,
        output_path
    )
