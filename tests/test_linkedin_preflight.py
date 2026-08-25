from teacher_agent.diagram import make_linkedin_cover
from teacher_agent.linkedin_preflight import preflight_linkedin_package


def good_package():
    return {
        'title': 'Robotics Class 1: What Is a Robot?',
        'description': 'Learn the sense-think-act model with a worked example and a tested Python lab.',
        'commentary': (
            'What actually makes a machine a robot?\n\n'
            'Today we build a practical mental model and test it in Python.\n\n'
            '• Understand sensing, decision-making, and action\n'
            '• Work through a numerical example\n'
            '• Predict a program result before running it\n'
            '• Connect the idea to real mobile robots\n\n'
            'Try the lab, change one assumption, and explain why the behavior changes. '
            'That explanation matters more than simply getting the code to run.\n\n'
            '#Robotics #Python #STEM #RobotLearning'
        ),
        'thumbnail_alt_text': 'Professor OS cover for Robotics Class 1: What Is a Robot?',
        'source': 'https://github.com/2vin/professor-os/blob/main/lessons/001/README.md',
    }


def test_preflight_accepts_premium_package(tmp_path):
    hero = tmp_path / 'hero.png'
    make_linkedin_cover(1, 'What Is a Robot?', 'robot, autonomy, sensors', hero)
    report = preflight_linkedin_package(good_package(), hero)
    assert report['passed'], report['errors']
    assert report['thumbnail_width'] == 1200
    assert report['thumbnail_height'] == 675


def test_preflight_rejects_invalid_source(tmp_path):
    hero = tmp_path / 'hero.png'
    make_linkedin_cover(1, 'What Is a Robot?', 'robot', hero)
    package = good_package()
    package['source'] = 'not-public'
    report = preflight_linkedin_package(package, hero)
    assert not report['passed']
