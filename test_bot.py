#!/usr/bin/env python3
"""
ملف اختبار بوت تيليجرام تيكنو
"""
import sys
import os
import asyncio
import logging

# إضافة مسار src إلى Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bot.config.settings import settings
from bot.database.database import db_manager
from bot.ai_integration.gemini_client import gemini_client

# إعداد نظام التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_database_connection():
    """اختبار الاتصال بقاعدة البيانات"""
    try:
        logger.info("اختبار الاتصال بقاعدة البيانات...")
        
        # اختبار الاتصال
        if db_manager.test_connection():
            logger.info("✅ تم الاتصال بقاعدة البيانات بنجاح")
            return True
        else:
            logger.error("❌ فشل في الاتصال بقاعدة البيانات")
            return False
            
    except Exception as e:
        logger.error(f"❌ خطأ في اختبار قاعدة البيانات: {e}")
        return False

async def test_gemini_client():
    """اختبار عميل Gemini AI"""
    try:
        logger.info("اختبار عميل Gemini AI...")
        
        # في وضع الاختبار، نتجاهل اختبار Gemini AI الحقيقي
        if settings.GEMINI_API_KEY.startswith("test_"):
            logger.info("✅ تم تجاهل اختبار Gemini AI في وضع الاختبار")
            return True
        
        # اختبار بسيط
        response = await gemini_client.generate_response("مرحبا")
        if response:
            logger.info("✅ عميل Gemini AI يعمل بشكل صحيح")
            return True
        else:
            logger.warning("⚠️ عميل Gemini AI لا يستجيب")
            return False
            
    except Exception as e:
        logger.error(f"❌ خطأ في اختبار Gemini AI: {e}")
        return False

async def test_settings_validation():
    """اختبار التحقق من الإعدادات"""
    try:
        logger.info("اختبار التحقق من الإعدادات...")
        
        if settings.validate_required_settings():
            logger.info("✅ جميع الإعدادات المطلوبة متوفرة")
            return True
        else:
            logger.error("❌ بعض الإعدادات المطلوبة مفقودة")
            return False
            
    except Exception as e:
        logger.error(f"❌ خطأ في اختبار الإعدادات: {e}")
        return False

async def test_imports():
    """اختبار استيراد الوحدات"""
    try:
        logger.info("اختبار استيراد الوحدات...")
        
        # اختبار استيراد الوحدات الأساسية
        from bot.handlers.command_handlers import command_handlers
        from bot.modules.member_management import member_manager
        from bot.modules.content_filtering import content_filter
        from bot.admin_interface.admin_panel import admin_panel
        
        logger.info("✅ تم استيراد جميع الوحدات بنجاح")
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ في استيراد الوحدات: {e}")
        return False

async def run_tests():
    """تشغيل جميع الاختبارات"""
    logger.info("🚀 بدء اختبارات بوت تيكنو...")
    
    tests = [
        ("التحقق من الإعدادات", test_settings_validation),
        ("استيراد الوحدات", test_imports),
        ("الاتصال بقاعدة البيانات", test_database_connection),
        ("عميل Gemini AI", test_gemini_client),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info(f"\n--- اختبار: {test_name} ---")
        try:
            result = await test_func()
            if result:
                passed += 1
                logger.info(f"✅ {test_name}: نجح")
            else:
                failed += 1
                logger.error(f"❌ {test_name}: فشل")
        except Exception as e:
            failed += 1
            logger.error(f"❌ {test_name}: خطأ - {e}")
    
    logger.info(f"\n📊 نتائج الاختبارات:")
    logger.info(f"✅ نجح: {passed}")
    logger.info(f"❌ فشل: {failed}")
    logger.info(f"📈 معدل النجاح: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        logger.info("🎉 جميع الاختبارات نجحت! البوت جاهز للتشغيل.")
        return True
    else:
        logger.warning("⚠️ بعض الاختبارات فشلت. يرجى مراجعة الأخطاء.")
        return False

if __name__ == "__main__":
    # تشغيل الاختبارات
    success = asyncio.run(run_tests())
    
    if success:
        print("\n✅ البوت جاهز للتشغيل!")
        print("لتشغيل البوت، استخدم: python3 src/main.py")
    else:
        print("\n❌ يرجى إصلاح الأخطاء قبل تشغيل البوت.")
        sys.exit(1)

