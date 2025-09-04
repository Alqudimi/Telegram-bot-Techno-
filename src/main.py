"""
الملف الرئيسي لبوت تيليجرام تيكنو
"""
import logging
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ChatMemberHandler, filters
)

# استيراد الوحدات المحلية
from bot.config.settings import settings
from bot.database.database import db_manager
from bot.handlers.command_handlers import command_handlers
from bot.modules.member_management import member_manager
from bot.modules.content_filtering import content_filter
from bot.admin_interface.admin_panel import admin_panel
from bot.ai_integration.gemini_client import gemini_client

# إعداد نظام التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    handlers=[
        logging.FileHandler('techno_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TechnoBot:
    """فئة البوت الرئيسية"""
    
    def __init__(self):
        """تهيئة البوت"""
        self.application = None
        self.is_running = False
    
    async def initialize(self):
        """تهيئة البوت والتحقق من الإعدادات"""
        try:
            # التحقق من الإعدادات المطلوبة
            if not settings.validate_required_settings():
                logger.error("فشل في التحقق من الإعدادات المطلوبة")
                return False
            
            # اختبار الاتصال بقاعدة البيانات
            if not db_manager.test_connection():
                logger.error("فشل في الاتصال بقاعدة البيانات")
                return False
            
            # إنشاء تطبيق البوت
            self.application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
            
            # تسجيل معالجات الأوامر
            await self._register_handlers()
            
            logger.info("تم تهيئة البوت بنجاح")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تهيئة البوت: {e}")
            return False
    
    async def _register_handlers(self):
        """تسجيل معالجات الأوامر والرسائل"""
        try:
            # معالجات الأوامر الأساسية
            self.application.add_handler(CommandHandler("start", command_handlers.start_command))
            self.application.add_handler(CommandHandler("help", command_handlers.help_command))
            self.application.add_handler(CommandHandler("setup", command_handlers.setup_command))
            self.application.add_handler(CommandHandler("stats", command_handlers.stats_command))
            
            # معالجات أوامر الإدارة
            self.application.add_handler(CommandHandler("ban", command_handlers.ban_command))
            self.application.add_handler(CommandHandler("unban", command_handlers.unban_command))
            self.application.add_handler(CommandHandler("mute", command_handlers.mute_command))
            self.application.add_handler(CommandHandler("unmute", command_handlers.unmute_command))
            
            # معالجات أوامر الذكاء الاصطناعي
            self.application.add_handler(CommandHandler("ask", command_handlers.ask_command))
            self.application.add_handler(CommandHandler("summarize", command_handlers.summarize_command))
            
            # معالجات إدارة المحتوى
            self.application.add_handler(CommandHandler("addword", command_handlers.addword_command))
            self.application.add_handler(CommandHandler("delword", command_handlers.delword_command))
            
            # معالجات الأعضاء الجدد والمغادرين
            self.application.add_handler(ChatMemberHandler(
                member_manager.handle_new_member, 
                ChatMemberHandler.CHAT_MEMBER
            ))
            
            # معالج الرسائل الجديدة (للترحيب والتصفية)
            self.application.add_handler(MessageHandler(
                filters.StatusUpdate.NEW_CHAT_MEMBERS,
                member_manager.handle_new_member
            ))
            
            self.application.add_handler(MessageHandler(
                filters.StatusUpdate.LEFT_CHAT_MEMBER,
                member_manager.handle_member_left
            ))
            
            # معالج تصفية المحتوى (لجميع الرسائل)
            self.application.add_handler(MessageHandler(
                filters.ALL & ~filters.COMMAND,
                self._message_filter_handler
            ))
            
            # معالج الاستعلامات المرتدة (للواجهة التفاعلية)
            self.application.add_handler(CallbackQueryHandler(admin_panel.handle_callback_query))
            
            # معالج التحقق من الأعضاء
            self.application.add_handler(CallbackQueryHandler(
                member_manager.handle_verification_callback,
                pattern=r"^verify_"
            ))
            
            # معالج الأخطاء
            self.application.add_error_handler(self._error_handler)
            
            logger.info("تم تسجيل جميع المعالجات بنجاح")
            
        except Exception as e:
            logger.error(f"خطأ في تسجيل المعالجات: {e}")
            raise
    
    async def _message_filter_handler(self, update: Update, context):
        """معالج تصفية الرسائل"""
        try:
            # تطبيق مرشحات المحتوى
            is_allowed = await content_filter.filter_message(update, context)
            
            if is_allowed:
                # تحديث نشاط المستخدم
                from bot.database.database import user_repo
                user_repo.update_user_activity(update.effective_user.id)
                user_repo.increment_user_messages(update.effective_user.id)
                
                # يمكن إضافة معالجات إضافية هنا
                # مثل الردود التلقائية، تحليل المشاعر، إلخ
                await self._handle_auto_responses(update, context)
            
        except Exception as e:
            logger.error(f"خطأ في معالج تصفية الرسائل: {e}")
    
    async def _handle_auto_responses(self, update: Update, context):
        """معالج الردود التلقائية"""
        try:
            message = update.message
            if not message or not message.text:
                return
            
            text = message.text.lower()
            chat_id = message.chat_id
            
            # الحصول على إعدادات المجموعة
            from bot.database.database import group_repo
            group_settings = group_repo.get_group_settings(chat_id)
            features = group_settings.get('features_enabled', settings.FEATURES)
            
            if not features.get('auto_responses', True):
                return
            
            # ردود تلقائية بسيطة
            auto_responses = {
                'مرحبا': 'مرحباً بك! 👋',
                'شكرا': 'العفو! 😊',
                'السلام عليكم': 'وعليكم السلام ورحمة الله وبركاته 🌸',
                'صباح الخير': 'صباح النور! ☀️',
                'مساء الخير': 'مساء النور! 🌙',
                'كيف الحال': 'الحمد لله، كيف حالك أنت؟ 😊',
                'ما اخبارك': 'بخير والحمد لله، وأنت؟ 🙂'
            }
            
            for trigger, response in auto_responses.items():
                if trigger in text:
                    await message.reply_text(response)
                    break
            
            # استخدام الذكاء الاصطناعي للردود المتقدمة
            if features.get('ai_integration', True):
                # فحص إذا كانت الرسالة تحتوي على سؤال
                question_indicators = ['؟', 'كيف', 'ماذا', 'متى', 'أين', 'لماذا', 'هل']
                if any(indicator in text for indicator in question_indicators):
                    # إرسال إشارة "يكتب..."
                    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
                    
                    # الحصول على رد من الذكاء الاصطناعي
                    ai_response = await gemini_client.generate_response(
                        text, 
                        f"أنت مساعد ذكي في مجموعة تيليجرام. أجب بإيجاز ومفيد."
                    )
                    
                    if ai_response and len(ai_response) < 500:  # تجنب الردود الطويلة
                        await message.reply_text(f"🤖 {ai_response}")
            
        except Exception as e:
            logger.error(f"خطأ في معالج الردود التلقائية: {e}")
    
    async def _error_handler(self, update: Update, context):
        """معالج الأخطاء العام"""
        try:
            logger.error(f"خطأ في البوت: {context.error}")
            
            # إرسال رسالة خطأ للمستخدم إذا أمكن
            if update and update.effective_chat:
                try:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="❌ حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى."
                    )
                except:
                    pass  # تجاهل الأخطاء في إرسال رسالة الخطأ
            
        except Exception as e:
            logger.error(f"خطأ في معالج الأخطاء: {e}")
    
    async def start(self):
        """بدء تشغيل البوت"""
        try:
            if not await self.initialize():
                logger.error("فشل في تهيئة البوت")
                return False
            
            logger.info("بدء تشغيل بوت تيكنو...")
            
            # بدء البوت
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
            
            self.is_running = True
            logger.info("تم بدء تشغيل البوت بنجاح! 🚀")
            
            # إبقاء البوت يعمل
            while self.is_running:
                await asyncio.sleep(1)
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في بدء تشغيل البوت: {e}")
            return False
    
    async def stop(self):
        """إيقاف البوت"""
        try:
            logger.info("إيقاف البوت...")
            self.is_running = False
            
            if self.application:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
            
            logger.info("تم إيقاف البوت بنجاح")
            
        except Exception as e:
            logger.error(f"خطأ في إيقاف البوت: {e}")

async def main():
    """الدالة الرئيسية"""
    try:
        # إنشاء مثيل البوت
        bot = TechnoBot()
        
        # بدء تشغيل البوت
        await bot.start()
        
    except KeyboardInterrupt:
        logger.info("تم إيقاف البوت بواسطة المستخدم")
    except Exception as e:
        logger.error(f"خطأ في الدالة الرئيسية: {e}")
    finally:
        if 'bot' in locals():
            await bot.stop()

if __name__ == "__main__":
    # تشغيل البوت
    asyncio.run(main())

