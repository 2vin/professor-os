from teacher_agent.media_curator import license_is_safe_for_public_reuse, append_media_resources


def meta(name, value):
    return {name: {'value': value}}


def test_license_filter_allows_cc_by_but_not_sharealike_or_nc():
    assert license_is_safe_for_public_reuse(meta('LicenseShortName', 'CC BY 4.0'))
    assert not license_is_safe_for_public_reuse(meta('LicenseShortName', 'CC BY-SA 4.0'))
    assert not license_is_safe_for_public_reuse(meta('LicenseShortName', 'CC BY-NC 4.0'))


def test_license_filter_allows_public_domain():
    assert license_is_safe_for_public_reuse(meta('Copyrighted', 'False'))


def test_append_media_resource_before_next_class():
    md = '## Further Learning\nRead more.\n\n## Next Class\nTomorrow.'
    media = {'items': [{
        'kind': 'video', 'title': 'Robot demo', 'source_page': 'https://commons.wikimedia.org/wiki/File:X',
        'attribution': 'A', 'license': 'CC BY 4.0'
    }]}
    updated = append_media_resources(md, media)
    assert '### Open Media Resource' in updated
    assert updated.index('### Open Media Resource') < updated.index('## Next Class')


def test_cc_by_candidate_requires_real_attribution(monkeypatch):
    from teacher_agent import media_curator
    page = {
        'title': 'File:Robot.jpg',
        'imageinfo': [{
            'width': 1600, 'height': 900, 'mime': 'image/jpeg', 'mediatype': 'BITMAP',
            'descriptionurl': 'https://commons.wikimedia.org/wiki/File:Robot.jpg',
            'thumburl': 'https://upload.wikimedia.org/robot.jpg',
            'extmetadata': {
                'LicenseShortName': {'value': 'CC BY 4.0'},
                'LicenseUrl': {'value': 'https://creativecommons.org/licenses/by/4.0/'},
                'Artist': {'value': ''},
                'Attribution': {'value': ''},
            }
        }]
    }
    assert media_curator._build_candidate(page, 'image') is None


def test_google_discovered_source_requires_explicit_safe_license():
    from teacher_agent import media_curator
    html = '<html><head><meta name="author" content="Jane Engineer"><link rel="license" href="https://creativecommons.org/licenses/by/4.0/"></head></html>'
    license_url, author = media_curator._extract_page_license(html)
    assert license_url == 'https://creativecommons.org/licenses/by/4.0/'
    assert author == 'Jane Engineer'
    assert media_curator._safe_license_url(license_url)


def test_unsafe_sharealike_license_is_rejected():
    from teacher_agent import media_curator
    assert not media_curator._safe_license_url('https://creativecommons.org/licenses/by-sa/4.0/')


def test_youtube_marker_is_added_for_embeddable_video():
    media = {
        'items': [{
            'kind': 'video', 'provider': 'YouTube', 'video_id': 'M7lc1UVf-VE',
            'title': 'Robot demonstration', 'source_page': 'https://www.youtube.com/watch?v=M7lc1UVf-VE',
            'attribution': 'Expert Robotics Channel', 'usage_mode': 'embed'
        }],
        'insert_after_heading': '## Real Robot Connection',
    }
    md = '## Real Robot Connection\nA robot example.\n\n## Vocabulary\nrobot'
    updated = append_media_resources(md, media)
    assert '<!-- PROFESSOR_OS_YOUTUBE:M7lc1UVf-VE -->' in updated
    assert 'Robot demonstration' in updated
