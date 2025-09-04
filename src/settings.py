"""
إعدادات مشروع بوت تيليجرام تيكنو
"""
import os
from typing import Optional
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

class Settings:
    """فئة إعدادات المشروع"""
    
    # إعدادات تيليجرام
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    BOT_NAME: str = os.getenv("BOT_NAME", "Techno")
    BOT_USERNAME: str = os.getenv("BOT_USERNAME", "techno_bot")
    
    # إعدادات Gemini AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # إعدادات قاعدة البيانات
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/techno_bot_db")
    
    # إعدادات Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # إعدادات التطبيق
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret_key_change_in_production")
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "default_encryption_key_change_in_production")
    
    # إعدادات الخدمات الخارجية
    RSS_FEEDS_ENABLED: bool = os.getenv("RSS_FEEDS_ENABLED", "True").lower() == "true"
    TWITTER_API_KEY: Optional[str] = os.getenv("TWITTER_API_KEY")
    YOUTUBE_API_KEY: Optional[str] = os.getenv("YOUTUBE_API_KEY")
    
    # إعدادات الأداء
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "10"))
    RATE_LIMIT_MESSAGES_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_MESSAGES_PER_MINUTE", "30"))
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
    
    # إعدادات الأمان
    ADMIN_USER_IDS: list = []  # سيتم تحديدها من قاعدة البيانات
    SUPER_ADMIN_USER_ID: Optional[int] = None  # سيتم تحديدها من قاعدة البيانات
    
    # إعدادات الميزات
    FEATURES = {
        "member_management": True,
        "content_filtering": True,
        "ai_integration": True,
        "admin_interface": True,
        "analytics": True,
        "scheduled_messages": True,
        "polls_surveys": True,
        "multi_language": True,
        "external_integrations": True,
        "backup_restore": True
    }
    
    # إعدادات اللغات المدعومة
    SUPPORTED_LANGUAGES = {
        "ar": "العربية",
        "en": "English",
        "es": "Español",
        "fr": "Français",
        "de": "Deutsch",
        "it": "Italiano",
        "ru": "Русский",
        "tr": "Türkçe"
    }
    
    # إعدادات التصفية
    DEFAULT_FILTER_SETTINGS = {
        "filter_links": True,
        "filter_media": False,
        "filter_stickers": False,
        "filter_voice": False,
        "filter_documents": False,
        "anti_spam": True,
        "profanity_filter": True,
        "flood_protection": True
    }
    
    @classmethod
    def validate_required_settings(cls) -> bool:
        """التحقق من وجود الإعدادات المطلوبة"""
        required_settings = [
            cls.TELEGRAM_BOT_TOKEN,
            cls.GEMINI_API_KEY,
            cls.DATABASE_URL
        ]
        
        missing_settings = []
        if not cls.TELEGRAM_BOT_TOKEN:
            missing_settings.append("TELEGRAM_BOT_TOKEN")
        if not cls.GEMINI_API_KEY:
            missing_settings.append("GEMINI_API_KEY")
        if not cls.DATABASE_URL:
            missing_settings.append("DATABASE_URL")
            
        if missing_settings:
            print(f"خطأ: الإعدادات المطلوبة التالية مفقودة: {', '.join(missing_settings)}")
            return False
        
        return True

# إنشاء مثيل الإعدادات
settings = Settings()

