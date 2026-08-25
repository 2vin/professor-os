from pathlib import Path

from teacher_agent.publication_gate import final_publication_gate


def _png(path, width=1200, height=675):
    import struct
    # Minimal header sufficient for dimension inspection plus padding for size sanity.
    data = b'\x89PNG\r\n\x1a\n' + b'\x00\x00\x00\x0dIHDR' + struct.pack('>II', width, height) + b'0' * 12000
    Path(path).write_bytes(data)


def test_publication_gate_passes_complete_package(tmp_path):
    lesson = {'class_no': 1, 'title': 'What Is a Robot?'}
    (tmp_path / 'README.md').write_text('# Class 1: What Is a Robot?', encoding='utf-8')
    article = '<html><head><meta name="viewport" content="width=device-width"><style>body{font-family:Arial}@media(max-width:700px){}</style></head><body><article>Professor OS Built by Connect.Vin What Is a Robot? <img src="hero.png"></article></body></html>' + ('x' * 5000)
    (tmp_path / 'index.html').write_text(article, encoding='utf-8')
    preview = '<html><head><meta name="viewport" content="width=device-width"><style>body{font-family:Arial}@media(max-width:700px){}</style></head><body>What Is a Robot? <img src="hero.png"></body></html>' + ('x' * 5000)
    (tmp_path / 'linkedin_preview.html').write_text(preview, encoding='utf-8')
    _png(tmp_path / 'hero.png')
    _png(tmp_path / 'diagram.png')
    (tmp_path / 'QUALITY_REPORT.json').write_text('{}', encoding='utf-8')
    (tmp_path / 'LINKEDIN_PREFLIGHT.json').write_text('{}', encoding='utf-8')
    (tmp_path / 'MEDIA_CREDITS.md').write_text('# Media Credits', encoding='utf-8')
    code = tmp_path / 'lab.py'
    code.write_text('print(1)', encoding='utf-8')
    report = final_publication_gate(
        lesson, tmp_path, {'passed': True}, {'passed': True, 'title': lesson['title']}, {'used': False, 'items': []}, [code])
    assert report['passed'] is True
    assert (tmp_path / 'PUBLICATION_GATE.json').exists()


def test_publication_gate_blocks_missing_artifacts(tmp_path):
    report = final_publication_gate(
        {'class_no': 1, 'title': 'Intro'}, tmp_path, {'passed': True}, {'passed': True}, {'used': False, 'items': []}, [])
    assert report['passed'] is False
    assert report['errors']
