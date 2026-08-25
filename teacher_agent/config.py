from dotenv import load_dotenv
import os

load_dotenv()


def _as_int(name, default):
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _as_float(name, default):
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


class Settings(object):
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-5')
        self.openai_timeout = _as_int('OPENAI_TIMEOUT', 180)
        self.api_max_attempts = max(1, _as_int('API_MAX_ATTEMPTS', 5))
        self.api_retry_base_delay = max(0.2, _as_float('API_RETRY_BASE_DELAY', 2.0))

        # Gemini-native image generation for premium lesson visuals.
        self.gemini_api_key = os.getenv('GEMINI_API_KEY', '')
        self.use_gemini_images = os.getenv('USE_GEMINI_IMAGES', 'true').lower() == 'true'
        self.gemini_image_model = os.getenv('GEMINI_IMAGE_MODEL', 'gemini-3.1-flash-lite-image')
        self.gemini_image_timeout = _as_int('GEMINI_IMAGE_TIMEOUT', 180)

        self.github_token = os.getenv('GITHUB_TOKEN', '')
        self.github_owner = os.getenv('GITHUB_OWNER', '')
        self.github_repo = os.getenv('GITHUB_REPO', 'robotics-classroom')
        self.github_branch = os.getenv('GITHUB_BRANCH', 'main')

        self.auto_sync_source = os.getenv('AUTO_SYNC_SOURCE', 'true').lower() == 'true'
        self.source_sync_interval = max(15, _as_int('SOURCE_SYNC_INTERVAL', 60))

        self.linkedin_access_token = os.getenv('LINKEDIN_ACCESS_TOKEN', '')
        self.linkedin_author_urn = os.getenv('LINKEDIN_AUTHOR_URN', '')
        self.linkedin_version = os.getenv('LINKEDIN_VERSION', '202607')

        self.public_lesson_base_url = os.getenv('PUBLIC_LESSON_BASE_URL', '')
        self.auto_publish = os.getenv('AUTO_PUBLISH', 'false').lower() == 'true'
        self.timezone = os.getenv('TIMEZONE', 'Asia/Kolkata')
        self.nightly_release_hour = max(0, min(23, _as_int('NIGHTLY_RELEASE_HOUR', 21)))
        self.nightly_release_minute = max(0, min(59, _as_int('NIGHTLY_RELEASE_MINUTE', 0)))

        # Premium publication quality gate.
        self.premium_quality_min_score = max(1, min(100, _as_int('PREMIUM_QUALITY_MIN_SCORE', 88)))
        self.premium_quality_min_dimension = max(1, min(100, _as_int('PREMIUM_QUALITY_MIN_DIMENSION', 80)))
        self.premium_quality_rewrite_rounds = max(0, min(4, _as_int('PREMIUM_QUALITY_REWRITE_ROUNDS', 2)))
        self.post_media_repair_rounds = max(0, min(3, _as_int('POST_MEDIA_REPAIR_ROUNDS', 2)))
        self.technical_quality_repair_rounds = max(0, min(5, _as_int('TECHNICAL_QUALITY_REPAIR_ROUNDS', 3)))
        self.require_ai_quality_review = os.getenv('REQUIRE_AI_QUALITY_REVIEW', 'true').lower() == 'true'

        # Premium real-world media enrichment. Search is discovery; reuse rights are still verified.
        self.enable_external_media = os.getenv('ENABLE_EXTERNAL_MEDIA', 'true').lower() == 'true'
        self.external_media_max_items = max(0, min(4, _as_int('EXTERNAL_MEDIA_MAX_ITEMS', 3)))
        self.external_media_min_width = max(640, _as_int('EXTERNAL_MEDIA_MIN_WIDTH', 1200))
        self.prefer_real_photos = os.getenv('PREFER_REAL_PHOTOS', 'true').lower() == 'true'
        self.require_recommended_media = os.getenv('REQUIRE_RECOMMENDED_MEDIA', 'true').lower() == 'true'

        # Google Programmable Search can discover real photographs with usage-right filters.
        # A Google result is never trusted by itself: the source page must expose a reusable license.
        self.google_image_search_enabled = os.getenv('GOOGLE_IMAGE_SEARCH_ENABLED', 'true').lower() == 'true'
        self.google_cse_api_key = os.getenv('GOOGLE_CSE_API_KEY', os.getenv('GOOGLE_API_KEY', ''))
        self.google_cse_id = os.getenv('GOOGLE_CSE_ID', '')

        # YouTube videos remain hosted by YouTube and are embedded only when the uploader allows embedding.
        self.youtube_media_enabled = os.getenv('YOUTUBE_MEDIA_ENABLED', 'true').lower() == 'true'
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY', os.getenv('GOOGLE_API_KEY', ''))
        self.youtube_max_results = max(1, min(15, _as_int('YOUTUBE_MAX_RESULTS', 8)))
        trusted = os.getenv(
            'YOUTUBE_TRUSTED_CHANNELS',
            'MIT OpenCourseWare,NASA,NASA JPL,Stanford Online,MathWorks,NVIDIA Developer,Open Robotics,Boston Dynamics,ETH Zurich,The Construct,Articulated Robotics')
        self.youtube_trusted_channels = [item.strip().lower() for item in trusted.split(',') if item.strip()]

        # LinkedIn publication preflight.
        self.linkedin_require_thumbnail = os.getenv('LINKEDIN_REQUIRE_THUMBNAIL', 'true').lower() == 'true'
        self.linkedin_commentary_soft_limit = max(500, _as_int('LINKEDIN_COMMENTARY_SOFT_LIMIT', 1800))

        self.dashboard_host = os.getenv('DASHBOARD_HOST', '127.0.0.1')
        # Cloud hosts such as Render inject PORT dynamically. Prefer it when present.
        self.dashboard_port = _as_int('PORT', _as_int('DASHBOARD_PORT', 8765))
        self.dashboard_schedule = os.getenv('DASHBOARD_SCHEDULE', 'true').lower() == 'true'
        # Local builds may bootstrap the first lesson automatically. Cloud web instances should not:
        # free instances can restart/sleep, and a restart must never spend AI credits.
        self.auto_bootstrap_generation = os.getenv('AUTO_BOOTSTRAP_GENERATION', 'true').lower() == 'true'
        # /api/run is convenient locally but must be disabled on a public unauthenticated deployment.
        self.enable_manual_run = os.getenv('ENABLE_MANUAL_RUN', 'true').lower() == 'true'


settings = Settings()
