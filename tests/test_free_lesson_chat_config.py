from teacher_agent.config import settings


def test_on_device_tutor_has_no_remote_credentials():
    assert settings.lesson_chat_enabled is True
    assert settings.lesson_chat_provider == 'qwen_on_device'
    assert settings.lesson_chat_model == 'Qwen3-0.6B-ONNX-q4'
    assert settings.lesson_chat_gemini_api_key == ''
    assert settings.lesson_chat_fallback_model == 'none'
