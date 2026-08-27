import html
import re
from pathlib import Path


def _inline_markup(text):
    """Render inline Markdown while preserving LaTeX delimiters for MathJax."""
    escaped = html.escape(str(text), quote=False)
    protected = []

    def protect_code(match):
        token = '@@PROFOS_CODE_{0}@@'.format(len(protected))
        protected.append('<code>{0}</code>'.format(match.group(1)))
        return token

    escaped = re.sub(r'`([^`]+)`', protect_code, escaped)
    escaped = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', escaped)
    escaped = re.sub(
        r'\[([^\]]+)\]\((https?://[^\s)]+)\)',
        r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>',
        escaped
    )
    escaped = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', escaped)

    for index, value in enumerate(protected):
        escaped = escaped.replace('@@PROFOS_CODE_{0}@@'.format(index), value)
    return escaped


def _is_table_separator(line):
    stripped = line.strip().strip('|')
    if not stripped:
        return False
    cells = [cell.strip() for cell in stripped.split('|')]
    if not cells:
        return False
    for cell in cells:
        if not re.match(r'^:?-{3,}:?$', cell):
            return False
    return True


def _split_table_row(line):
    return [cell.strip() for cell in line.strip().strip('|').split('|')]


def _render_table(rows):
    if len(rows) < 2:
        return ''
    header = _split_table_row(rows[0])
    body_rows = [_split_table_row(row) for row in rows[2:]]
    out = ['<div class="table-scroll"><table><thead><tr>']
    for cell in header:
        out.append('<th>{0}</th>'.format(_inline_markup(cell)))
    out.append('</tr></thead><tbody>')
    for row in body_rows:
        out.append('<tr>')
        for index in range(len(header)):
            value = row[index] if index < len(row) else ''
            out.append('<td>{0}</td>'.format(_inline_markup(value)))
        out.append('</tr>')
    out.append('</tbody></table></div>')
    return ''.join(out)


def _render_math_block(expression):
    expression = str(expression or '').strip()
    return (
        '<div class="math-block" role="group" aria-label="Mathematical expression">'
        '<span class="math-source">\\[{0}\\]</span>'
        '</div>'
    ).format(html.escape(expression, quote=False))


def markdown_to_html(markdown):
    lines = str(markdown or '').splitlines()
    out = []
    paragraph = []
    list_type = None
    in_code = False
    code_lines = []
    code_lang = ''
    index = 0

    def flush_paragraph():
        if paragraph:
            text = ' '.join(item.strip() for item in paragraph if item.strip())
            if text:
                out.append('<p>{0}</p>'.format(_inline_markup(text)))
            del paragraph[:]

    def close_list():
        nonlocal list_type
        if list_type:
            out.append('</{0}>'.format(list_type))
            list_type = None

    while index < len(lines):
        line = lines[index].rstrip('\n')
        stripped = line.strip()

        if in_code:
            if stripped.startswith('```'):
                code = '\n'.join(code_lines)
                out.append(
                    '<div class="code-card"><div class="code-label">{0}</div>'
                    '<pre><code>{1}</code></pre></div>'.format(
                        html.escape(code_lang or 'code'), html.escape(code)
                    )
                )
                code_lines = []
                code_lang = ''
                in_code = False
            else:
                code_lines.append(line)
            index += 1
            continue

        if stripped.startswith('```'):
            flush_paragraph()
            close_list()
            in_code = True
            code_lang = stripped[3:].strip()
            index += 1
            continue

        youtube_match = re.match(
            r'^<!--\s*PROFESSOR_OS_YOUTUBE:([A-Za-z0-9_-]{6,})\s*-->$',
            stripped
        )
        if youtube_match:
            flush_paragraph()
            close_list()
            video_id = html.escape(youtube_match.group(1), quote=True)
            out.append(
                '<div class="video-card"><div class="video-frame">'
                '<iframe src="https://www.youtube.com/embed/{0}" '
                'title="Embedded YouTube teaching video" frameborder="0" '
                'allow="accelerometer; autoplay; clipboard-write; encrypted-media; '
                'gyroscope; picture-in-picture; web-share" '
                'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen>'
                '</iframe></div></div>'.format(video_id)
            )
            index += 1
            continue

        if stripped == r'\[' or stripped == '$$':
            flush_paragraph()
            close_list()
            closing = r'\]' if stripped == r'\[' else '$$'
            math_lines = []
            index += 1
            while index < len(lines) and lines[index].strip() != closing:
                math_lines.append(lines[index])
                index += 1
            if index < len(lines):
                index += 1
            out.append(_render_math_block('\n'.join(math_lines)))
            continue

        single_math = re.match(r'^\\\[(.*)\\\]$', stripped)
        if single_math:
            flush_paragraph()
            close_list()
            out.append(_render_math_block(single_math.group(1)))
            index += 1
            continue

        if '|' in stripped and index + 1 < len(lines) and _is_table_separator(lines[index + 1]):
            flush_paragraph()
            close_list()
            rows = [line, lines[index + 1]]
            index += 2
            while index < len(lines):
                candidate = lines[index]
                if not candidate.strip() or '|' not in candidate:
                    break
                rows.append(candidate)
                index += 1
            out.append(_render_table(rows))
            continue

        if not stripped:
            flush_paragraph()
            close_list()
            index += 1
            continue

        if stripped in ('---', '***', '___'):
            flush_paragraph()
            close_list()
            out.append('<hr>')
            index += 1
            continue

        if line.startswith('# '):
            flush_paragraph(); close_list()
            out.append('<h1>{0}</h1>'.format(_inline_markup(line[2:].strip())))
            index += 1; continue
        if line.startswith('## '):
            flush_paragraph(); close_list()
            out.append('<h2>{0}</h2>'.format(_inline_markup(line[3:].strip())))
            index += 1; continue
        if line.startswith('### '):
            flush_paragraph(); close_list()
            out.append('<h3>{0}</h3>'.format(_inline_markup(line[4:].strip())))
            index += 1; continue

        image_match = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)\s*$', stripped)
        if image_match:
            flush_paragraph(); close_list()
            alt = html.escape(image_match.group(1) or 'Teaching visual')
            src = html.escape(image_match.group(2), quote=True)
            out.append('<figure><img loading="lazy" src="{0}" alt="{1}"></figure>'.format(src, alt))
            index += 1
            continue

        if stripped.startswith('>'):
            flush_paragraph(); close_list()
            quote_lines = []
            while index < len(lines) and lines[index].strip().startswith('>'):
                quote_lines.append(re.sub(r'^\s*>\s?', '', lines[index]).strip())
                index += 1
            out.append('<blockquote>{0}</blockquote>'.format(_inline_markup(' '.join(quote_lines))))
            continue

        unordered = re.match(r'^[-*]\s+(.+)$', stripped)
        ordered = re.match(r'^\d+[.)]\s+(.+)$', stripped)
        if unordered or ordered:
            flush_paragraph()
            desired = 'ul' if unordered else 'ol'
            if list_type != desired:
                close_list()
                out.append('<{0}>'.format(desired))
                list_type = desired
            item = unordered.group(1) if unordered else ordered.group(1)
            out.append('<li>{0}</li>'.format(_inline_markup(item)))
            index += 1
            continue

        if stripped.lower().startswith('**figure:**'):
            flush_paragraph(); close_list()
            out.append('<p class="figure-caption">{0}</p>'.format(_inline_markup(stripped)))
            index += 1
            continue

        paragraph.append(line)
        index += 1

    flush_paragraph()
    close_list()
    if in_code:
        code = '\n'.join(code_lines)
        out.append('<div class="code-card"><pre><code>{0}</code></pre></div>'.format(html.escape(code)))
    return '\n'.join(out)


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


def render_premium_article(markdown, lesson, output_path, hero_filename='hero.png', quality_report=None, navigation=None):
    body = markdown_to_html(markdown)
    class_no = int(lesson['class_no'])
    title = str(lesson['title'])
    concepts = str(lesson.get('concepts', '') or '')
    category = _category_for_class(class_no)
    reading_minutes = max(6, int(round(len(str(markdown).split()) / 190.0)))
    score = ((quality_report.get('ai') or {}).get('overall_score')) if quality_report else None
    quality_badge = 'Editorially validated' if score is None else 'Editorial score {0}/100'.format(score)
    concepts_short = concepts or 'Robotics concepts'
    if len(concepts_short) > 72:
        concepts_short = concepts_short[:69].rstrip(', ') + '...'

    navigation = navigation or {}
    previous_item = navigation.get('previous') or {}
    next_item = navigation.get('next') or {}
    previous_html = ''
    if previous_item:
        if previous_item.get('url'):
            previous_html = '<a class="navtile" href="{0}"><span>Previous stream</span><b>Class {1:02d} · {2}</b></a>'.format(
                html.escape(previous_item.get('url'), quote=True), int(previous_item.get('class_no') or 0), html.escape(str(previous_item.get('title') or 'Previous lesson')))
        else:
            previous_html = '<div class="navtile disabled"><span>Previous stream</span><b>Class {0:02d} · {1}</b></div>'.format(
                int(previous_item.get('class_no') or 0), html.escape(str(previous_item.get('title') or 'Previous lesson')))
    next_html = ''
    if next_item:
        if next_item.get('url'):
            next_html = '<a class="navtile next" href="{0}"><span>Continue learning</span><b>Class {1:02d} · {2}</b></a>'.format(
                html.escape(next_item.get('url'), quote=True), int(next_item.get('class_no') or 0), html.escape(str(next_item.get('title') or 'Next lesson')))
        else:
            next_html = '<a class="navtile next upcoming" href="/#tonight"><span>Coming next</span><b>Class {0:02d} · {1}</b><em>Nightly release</em></a>'.format(
                int(next_item.get('class_no') or 0), html.escape(str(next_item.get('title') or 'Next lesson')))

    page = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#060708">
<title>Class __CLASS__: __TITLE__ · Professor OS</title>
<script>
window.MathJax={tex:{inlineMath:[['\\(','\\)']],displayMath:[['\\[','\\]'],['$$','$$']],processEscapes:true},options:{skipHtmlTags:['script','noscript','style','textarea','pre','code']},svg:{fontCache:'global'}};
</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
<style>
:root{--bg:#060708;--panel:#0d1013;--line:#252b30;--line2:#363f46;--text:#f4f5f2;--soft:#bcc1bc;--muted:#747d7d;--acid:#caff4f;--acid2:#dbff86;--green:#88edaa;--shadow:0 26px 80px rgba(0,0,0,.46);--top:54px;--dock:72px;--reading:0%}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:80px}body{margin:0;background:radial-gradient(circle at 10% 0,rgba(202,255,79,.09),transparent 24%),linear-gradient(180deg,#060708,#0a0c0e);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}a{color:inherit;text-decoration:none}button{font:inherit}::selection{background:var(--acid);color:#111}
.reading-line{position:fixed;top:0;left:0;right:0;height:3px;z-index:150;background:rgba(255,255,255,.04)}.reading-line i{display:block;width:var(--reading);height:100%;background:linear-gradient(90deg,var(--acid),var(--acid2))}
.os-topbar{position:fixed;left:0;right:0;top:0;height:var(--top);z-index:100;display:grid;grid-template-columns:auto 1fr auto;gap:14px;align-items:center;padding:0 14px;border-bottom:1px solid rgba(54,63,70,.62);background:rgba(6,7,8,.90);backdrop-filter:blur(18px)}.brand{display:flex;align-items:center;gap:10px}.mark{width:30px;height:30px;border-radius:10px;background:linear-gradient(145deg,#1a2112,#11160d);border:1px solid rgba(202,255,79,.28);display:grid;place-items:center;font-weight:900}.brand b{font-size:11px;letter-spacing:.15em;text-transform:uppercase}.brand span{font-size:8px;color:var(--muted);letter-spacing:.11em;text-transform:uppercase}.crumb{justify-self:center;font-size:9px;letter-spacing:.11em;text-transform:uppercase;color:var(--muted)}.crumb b{color:var(--soft)}.top-actions{display:flex;gap:7px}.pill{display:inline-flex;align-items:center;padding:8px 10px;border:1px solid var(--line);border-radius:999px;background:#0d1013;font-size:8px;font-weight:800;letter-spacing:.09em;text-transform:uppercase;color:var(--soft)}
.dock{position:fixed;left:0;top:var(--top);bottom:0;width:var(--dock);z-index:90;border-right:1px solid rgba(54,63,70,.58);background:rgba(6,7,8,.92);display:flex;flex-direction:column;align-items:center;padding:14px 10px;gap:9px}.dock a{width:46px;height:46px;border:1px solid var(--line);border-radius:14px;background:#0d1013;color:var(--muted);display:grid;place-items:center;font-size:16px}.dock a.active{background:linear-gradient(135deg,var(--acid),var(--acid2));color:#111;border-color:transparent}.dock .spacer{flex:1}
.desktop{margin-left:var(--dock);padding-top:var(--top);min-height:100vh}.shell{max-width:1460px;margin:0 auto;padding:16px 16px 88px}.window{border:1px solid rgba(54,63,70,.78);border-radius:24px;background:linear-gradient(180deg,rgba(13,16,19,.98),rgba(9,11,13,.99));box-shadow:var(--shadow);overflow:hidden}.bar{height:46px;display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:12px;padding:0 14px;border-bottom:1px solid rgba(54,63,70,.62)}.dots{display:flex;gap:6px}.dots i{width:8px;height:8px;border-radius:50%;background:#353b3e}.dots i:nth-child(1){background:#7b4e54}.dots i:nth-child(2){background:#735f3f}.dots i:nth-child(3){background:#3d695a}.bar-title{font-size:9px;letter-spacing:.13em;text-transform:uppercase;color:var(--muted)}.bar-state{font-size:9px;letter-spacing:.1em;text-transform:uppercase;color:var(--soft)}
.hero{display:grid;grid-template-columns:minmax(0,.58fr) minmax(360px,.42fr);min-height:500px}.hero-copy{padding:28px;display:flex;flex-direction:column;justify-content:center}.eyebrow{font-size:9px;letter-spacing:.18em;text-transform:uppercase;color:var(--acid)}.hero h1{margin:16px 0 14px;font-size:clamp(44px,5vw,76px);line-height:.94;letter-spacing:-.055em;max-width:10ch}.lead{margin:0;color:var(--soft);font-size:14px;line-height:1.8;max-width:680px}.hero-meta{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-top:22px}.meta{padding:12px;border:1px solid var(--line);border-radius:13px;background:rgba(12,15,17,.76)}.meta span{display:block;font-size:7px;letter-spacing:.11em;text-transform:uppercase;color:var(--muted)}.meta b{display:block;margin-top:6px;font-size:12px;line-height:1.35}.hero-media{border-left:1px solid rgba(54,63,70,.62);background:#090b0d;min-height:430px}.hero-media img{width:100%;height:100%;object-fit:cover;display:block}
.reader{display:grid;grid-template-columns:300px minmax(0,1fr);gap:16px;margin-top:16px;align-items:start}.rail{position:sticky;top:70px;display:grid;gap:14px}.rail-window{padding:16px}.rail-window h3{margin:0 0 12px;font-size:12px;letter-spacing:.08em;text-transform:uppercase}.progress-row{display:flex;justify-content:space-between;gap:10px;font-size:10px;color:var(--muted)}.progress-row b{color:var(--text)}.track{height:8px;border-radius:999px;background:#11161a;border:1px solid var(--line);overflow:hidden;margin:10px 0}.track i{display:block;width:0;height:100%;background:linear-gradient(90deg,var(--acid),var(--acid2));border-radius:999px}.complete{width:100%;border:0;border-radius:11px;padding:11px 12px;background:linear-gradient(135deg,var(--acid),var(--acid2));color:#111;font-size:9px;font-weight:800;letter-spacing:.09em;text-transform:uppercase;cursor:pointer}.complete.done{background:linear-gradient(135deg,var(--green),var(--acid2))}.resume-note{display:none;margin-top:9px;font-size:10px;line-height:1.55;color:var(--muted)}.toc{display:grid;gap:6px}.toc a{display:block;padding:9px 10px;border:1px solid var(--line);border-radius:10px;background:rgba(12,15,17,.76);font-size:10px;color:var(--soft)}.toc a.active{border-color:var(--line2);color:var(--text);background:#11161a}.core{height:160px;border:1px solid var(--line);border-radius:14px;background:radial-gradient(circle at center,rgba(202,255,79,.08),transparent 34%),linear-gradient(180deg,#0d1013,#090b0d);position:relative;display:grid;place-items:center;overflow:hidden}.core:before,.core:after{content:"";position:absolute;border:1px solid rgba(202,255,79,.14);border-radius:50%;width:110px;height:110px}.core:after{width:160px;height:160px;border-color:rgba(219,255,134,.12)}.core i{width:72px;height:72px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#f4f5f2,#dbff86 24%,#59633d 58%,transparent 82%);box-shadow:0 18px 38px rgba(202,255,79,.10)}
.content-window{padding:28px}.content h1{font-size:40px;letter-spacing:-.045em}.content h2{margin:42px 0 14px;font-size:30px;letter-spacing:-.035em;line-height:1.08}.content h3{margin:27px 0 10px;font-size:21px;letter-spacing:-.02em}.content p,.content li,.content td,.content th{font-size:15px;line-height:1.82}.content p,.content li,.content td{color:var(--soft)}.content p{margin:0 0 16px}.content ul,.content ol{padding-left:22px}.content li{margin:8px 0}.content strong{color:var(--text)}.content a{color:#dfff96;text-decoration:underline;text-underline-offset:2px}.content code{font-size:.92em;padding:2px 6px;border-radius:7px;background:#090b0d;border:1px solid var(--line);color:#d8e0d4}.code-card{margin:22px 0;border:1px solid var(--line);border-radius:16px;overflow:hidden;background:#07090b}.code-label{padding:10px 13px;border-bottom:1px solid var(--line);font-size:8px;letter-spacing:.11em;text-transform:uppercase;color:var(--muted)}pre{margin:0;padding:16px;overflow:auto;line-height:1.65}pre code{padding:0;border:0;background:none;color:#e0e5dd}figure{margin:28px 0}figure img{display:block;width:100%;border-radius:16px;border:1px solid var(--line)}.figure-caption{margin-top:-16px!important;padding:0 4px;color:var(--muted)!important;font-size:12px!important}blockquote{margin:20px 0;padding:16px 18px;border-left:3px solid var(--acid);border-radius:0 14px 14px 0;background:rgba(202,255,79,.055);color:var(--text);font-size:15px;line-height:1.75}
.math-block{margin:22px 0;padding:18px 20px;border:1px solid var(--line);border-radius:16px;background:linear-gradient(180deg,#0b0f11,#080a0c);overflow-x:auto;text-align:center;color:var(--text);font-size:1.08rem;min-height:58px;display:flex;align-items:center;justify-content:center}.math-source{white-space:pre-wrap;overflow-wrap:anywhere}.math-block mjx-container{margin:0!important;max-width:100%;overflow-x:auto;overflow-y:hidden}.table-scroll{margin:22px 0;overflow-x:auto;border:1px solid var(--line);border-radius:16px;background:#090b0d}.table-scroll table{width:100%;border-collapse:collapse;min-width:620px}.table-scroll th{padding:12px 13px;text-align:left;background:#11161a;color:var(--text);font-weight:800;border-bottom:1px solid var(--line2)}.table-scroll td{padding:12px 13px;border-top:1px solid var(--line);vertical-align:top}hr{height:1px;border:0;background:var(--line);margin:34px 0}.video-card{margin:28px 0;border:1px solid var(--line);border-radius:16px;overflow:hidden}.video-frame{position:relative;width:100%;aspect-ratio:16/9}.video-frame iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.lessonnav{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:16px}.navtile{display:grid;gap:6px;padding:16px;border:1px solid rgba(54,63,70,.78);border-radius:18px;background:linear-gradient(180deg,rgba(13,16,19,.98),rgba(9,11,13,.99));box-shadow:var(--shadow)}.navtile:hover{border-color:var(--line2);transform:translateY(-2px)}.navtile span{font-size:8px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}.navtile b{font-size:14px;line-height:1.4}.navtile em{font-style:normal;font-size:10px;color:var(--muted)}.navtile.next{text-align:right}.navtile.disabled{opacity:.55}.footer{display:flex;justify-content:space-between;gap:12px;margin-top:16px;padding:14px 16px;border:1px solid var(--line);border-radius:16px;color:var(--muted);font-size:10px}.mobile-dock{display:none}
@media(max-width:1100px){.hero,.reader{grid-template-columns:1fr}.hero-media{border-left:0;border-top:1px solid rgba(54,63,70,.62);min-height:330px}.rail{position:static;grid-template-columns:repeat(2,minmax(0,1fr))}.hero-meta{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:760px){:root{--dock:0px}.dock{display:none}.desktop{margin-left:0}.os-topbar{grid-template-columns:auto 1fr}.crumb{display:none}.shell{padding:10px 10px 82px}.hero-copy,.content-window{padding:18px}.hero h1{font-size:40px}.rail{grid-template-columns:1fr}.hero-meta,.lessonnav{grid-template-columns:1fr}.navtile.next{text-align:left}.mobile-dock{position:fixed;left:10px;right:10px;bottom:10px;z-index:120;display:grid;grid-template-columns:1fr auto;gap:8px;align-items:center;padding:9px;border:1px solid var(--line2);border-radius:15px;background:rgba(6,7,8,.95);backdrop-filter:blur(16px)}.mobile-dock .mprogress{display:grid;gap:4px}.mobile-dock span{font-size:7px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}.mobile-dock b{font-size:10px}.mobile-dock .complete{width:auto;padding:10px}.table-scroll{margin-left:-4px;margin-right:-4px}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}html{scroll-behavior:auto}}
</style>
</head>
<body data-class="__CLASS_NUMBER__">
<div class="reading-line"><i></i></div>
<header class="os-topbar"><div class="brand"><div class="mark">π</div><div><b>Professor OS</b><br><span>Reader application</span></div></div><div class="crumb">ProfessorOS / Library / <b>CLS___CLASS_PADDED__</b></div><div class="top-actions"><a class="pill" href="/">Home</a><a class="pill" href="/#library">Library</a></div></header>
<nav class="dock"><a href="/">⌂</a><a href="/#library">▦</a><a class="active" href="#">R</a><div class="spacer"></div><a href="/#system">⚙</a></nav>
<main class="desktop"><div class="shell">
<section class="window"><div class="bar"><div class="dots"><i></i><i></i><i></i></div><div class="bar-title">Reader / Knowledge Stream</div><div class="bar-state">CLS___CLASS_PADDED__</div></div><div class="hero"><div class="hero-copy"><div class="eyebrow">Class __CLASS_PADDED__ · __CATEGORY__</div><h1>__TITLE__</h1><p class="lead">A focused Professor OS reading workspace. Learn the concept, inspect the visuals, run the code, and keep your position in the curriculum.</p><div class="hero-meta"><div class="meta"><span>Reading time</span><b>~__READING__ min</b></div><div class="meta"><span>Editorial quality</span><b>__QUALITY__</b></div><div class="meta"><span>Concepts</span><b>__CONCEPTS__</b></div><div class="meta"><span>State</span><b id="headerProgressState">In progress</b></div></div></div><div class="hero-media"><img src="__HERO__" alt="Professor OS lesson visual"></div></div></section>
<div class="reader"><aside class="rail"><section class="window rail-window"><h3>Reading progress</h3><div class="progress-row"><span>Progress</span><b id="readingPct">0%</b></div><div class="track"><i id="sideReadingBar"></i></div><button class="complete" id="completeBtn" type="button">Mark class complete</button><div class="resume-note" id="resumeNote"></div></section><section class="window rail-window"><h3>On this page</h3><nav class="toc" id="toc"></nav></section><section class="window rail-window"><h3>Lesson core</h3><div class="core"><i></i></div></section></aside><section class="window content-window"><article class="content" id="lessonContent">__BODY__</article></section></div>
<nav class="lessonnav">__PREVIOUS____NEXT__</nav><footer class="footer"><span>Professor OS · Learning Operating System</span><span>Built by Connect.Vin</span></footer>
</div></main>
<div class="mobile-dock"><div class="mprogress"><span>Reading progress</span><b id="mobilePct">0%</b><div class="track"><i id="mobileReadingBar"></i></div></div><button class="complete" id="mobileCompleteBtn" type="button">Complete</button></div>
<script>
(function(){var CLASS_NO=__CLASS_NUMBER__,KEY='professorOSStudentProgressV2';function read(){try{return JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){return {}}}function norm(s){s=s||{};if(!Array.isArray(s.completed))s.completed=[];if(!s.reading)s.reading={};return s}function save(s){localStorage.setItem(KEY,JSON.stringify(s))}function done(){return norm(read()).completed.indexOf(CLASS_NO)>=0}function paintDone(){var d=done();['completeBtn','mobileCompleteBtn'].forEach(function(id){var e=document.getElementById(id);if(e){e.textContent=id==='mobileCompleteBtn'?(d?'Done ✓':'Complete'):(d?'Completed ✓':'Mark class complete');e.classList.toggle('done',d)}});var h=document.getElementById('headerProgressState');if(h)h.textContent=d?'Completed':'In progress'}function toggle(){var s=norm(read()),i=s.completed.indexOf(CLASS_NO);if(i<0)s.completed.push(CLASS_NO);else s.completed.splice(i,1);s.lastOpened=CLASS_NO;s.lastUrl=location.pathname;s.lastTitle=document.title;save(s);paintDone()}function reading(){var h=document.documentElement,total=Math.max(1,h.scrollHeight-h.clientHeight),pct=Math.max(0,Math.min(100,Math.round(h.scrollTop/total*100)));document.documentElement.style.setProperty('--reading',pct+'%');['sideReadingBar','mobileReadingBar'].forEach(function(id){var e=document.getElementById(id);if(e)e.style.width=pct+'%'});['readingPct','mobilePct'].forEach(function(id){var e=document.getElementById(id);if(e)e.textContent=pct+'%'});var s=norm(read());s.reading[String(CLASS_NO)]=pct;s.lastOpened=CLASS_NO;s.lastUrl=location.pathname;s.lastTitle=document.title;save(s)}var timer=null;addEventListener('scroll',function(){if(timer)return;timer=setTimeout(function(){timer=null;reading()},120)},{passive:true});function toc(){var root=document.getElementById('toc'),heads=[].slice.call(document.querySelectorAll('#lessonContent h2,#lessonContent h3'));heads.forEach(function(h,i){h.id='section-'+(i+1);var a=document.createElement('a');a.href='#'+h.id;a.textContent=h.textContent;a.dataset.target=h.id;if(h.tagName==='H3')a.style.paddingLeft='18px';root.appendChild(a)});if('IntersectionObserver' in window){var o=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){[].slice.call(document.querySelectorAll('#toc a')).forEach(function(a){a.classList.toggle('active',a.dataset.target===e.target.id)})}})},{rootMargin:'-18% 0px -68% 0px'});heads.forEach(function(h){o.observe(h)})}}function resume(){var s=norm(read()),pct=Number(s.reading[String(CLASS_NO)]||0),note=document.getElementById('resumeNote');if(pct>5&&pct<96&&!done()){note.style.display='block';note.textContent='You previously reached '+pct+'%. Continue from the academy Home app.'}if(new URLSearchParams(location.search).get('resume')==='1'&&pct>5&&pct<98){setTimeout(function(){var total=Math.max(1,document.documentElement.scrollHeight-document.documentElement.clientHeight);scrollTo(0,total*pct/100)},260)}}document.getElementById('completeBtn').addEventListener('click',toggle);document.getElementById('mobileCompleteBtn').addEventListener('click',toggle);paintDone();reading();toc();resume();})();
</script></body></html>"""

    replacements = {
        '__CLASS__': str(class_no), '__CLASS_NUMBER__': str(class_no), '__CLASS_PADDED__': '{0:02d}'.format(class_no),
        '__TITLE__': html.escape(title), '__CATEGORY__': html.escape(category), '__READING__': str(reading_minutes),
        '__QUALITY__': html.escape(quality_badge), '__CONCEPTS__': html.escape(concepts_short), '__HERO__': html.escape(hero_filename, quote=True),
        '__BODY__': body, '__PREVIOUS__': previous_html, '__NEXT__': next_html,
    }
    for key, value in replacements.items():
        page = page.replace(key, value)
    output_path = Path(output_path)
    output_path.write_text(page, encoding='utf-8')
    return output_path


def render_linkedin_preview(package, output_path, hero_filename='hero.png'):
    commentary = html.escape(package.get('commentary', '')).replace('\n', '<br>')
    title = html.escape(package.get('title', ''))
    description = html.escape(package.get('description', ''))
    alt_text = html.escape(package.get('thumbnail_alt_text', ''), quote=True)
    hero = html.escape(hero_filename, quote=True)
    page = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LinkedIn Preflight</title><style>body{margin:0;background:#f3f6f9;font-family:Arial,sans-serif;color:#1d2226}.wrap{max-width:620px;margin:30px auto}.post{background:#fff;border:1px solid #d8d8d8;border-radius:12px;overflow:hidden;box-shadow:0 16px 40px rgba(0,0,0,.08)}.author{padding:15px 16px 8px;font-weight:700}.copy{padding:8px 16px 16px;font-size:14px;line-height:1.5}.post img{width:100%;aspect-ratio:16/9;object-fit:cover;display:block}.article{padding:12px 16px 15px;background:#f7f8f9;border-top:1px solid #e6e6e6}.article h2{font-size:15px;margin:0 0 6px}.article p{font-size:12px;color:#5e5e5e;margin:0;line-height:1.4}.note{font-size:12px;color:#6b6b6b;margin-bottom:10px}</style></head><body><div class="wrap"><div class="note">Local approximation for typography, spacing, and article-card preflight. LinkedIn controls the final platform font.</div><div class="post"><div class="author">Professor OS · Connect.Vin</div><div class="copy">__COMMENTARY__</div><img src="__HERO__" alt="__ALT__"><div class="article"><h2>__TITLE__</h2><p>__DESCRIPTION__</p></div></div></div></body></html>"""
    replacements = {'__COMMENTARY__': commentary, '__HERO__': hero, '__ALT__': alt_text, '__TITLE__': title, '__DESCRIPTION__': description}
    for key, value in replacements.items():
        page = page.replace(key, value)
    Path(output_path).write_text(page, encoding='utf-8')
    return output_path
