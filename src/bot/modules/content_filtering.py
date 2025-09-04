"""
وحدة تصفية المحتوى لبوت تيليجرام تيكنو
"""
import logging
import re
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List, Set
from urllib.parse import urlparse
from telegram import Update, Message
from telegram.ext import ContextTypes
from telegram.constants import MessageType

from ..database.database import group_repo, message_repo, db_manager
from ..database.models import MessageType as DBMessageType, Action, ActionType
from ..ai_integration.gemini_client import gemini_client
from ..config.settings import settings

logger = logging.getLogger(__name__)

class ContentFilter:
    """مرشح المحتوى"""
    
    def __init__(self):
        """تهيئة مرشح المحتوى"""
        self.spam_detection_cache = {}
        self.user_message_history = {}
        self.flood_protection = {}
        
        # قائمة الكلمات المحظورة الافتراضية
        self.default_banned_words = {
            'ar': ['كلمة محظورة1', 'كلمة محظورة2'],  # يمكن إضافة المزيد
            'en': ['spam', 'scam', 'fake'],
        }
        
        # قائمة النطاقات المشبوهة
        self.suspicious_domains = {
            'bit.ly', 'tinyurl.com', 't.me/joinchat', 'telegram.me/joinchat'
        }
        
        # أنماط الروابط المشبوهة
        self.suspicious_patterns = [
            r'(https?://)?bit\.ly/\w+',
            r'(https?://)?tinyurl\.com/\w+',
            r't\.me/joinchat/[\w-]+',
            r'telegram\.me/joinchat/[\w-]+',
            r'@\w+bot\b',  # البوتات
            r'\b\d{10,}\b',  # أرقام طويلة (ربما أرقام هواتف)
        ]
    
    async def filter_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """تصفية الرسالة الواردة"""
        try:
            message = update.message
            if not message:
                return True
            
            chat_id = message.chat_id
            user_id = message.from_user.id
            
            # الحصول على إعدادات التصفية للمجموعة
            group_settings = group_repo.get_group_settings(chat_id)
            filter_settings = group_settings.get('filter_settings', settings.DEFAULT_FILTER_SETTINGS)
            
            # تخطي المشرفين
            if await self._is_admin(update, context, user_id):
                return True
            
            # حماية من الفيضان (Flood Protection)
            if filter_settings.get('flood_protection', True):
                if await self._check_flood_protection(message):
                    await self._take_action(update, context, 'flood', 'إرسال رسائل بكثرة')
                    return False
            
            # فحص الرسائل المزعجة
            if filter_settings.get('anti_spam', True):
                spam_result = await self._check_spam(message)
                if spam_result['is_spam']:
                    await self._take_action(update, context, 'spam', f"رسالة مزعجة: {', '.join(spam_result['reasons'])}")
                    return False
            
            # فحص الكلمات المحظورة
            if filter_settings.get('profanity_filter', True):
                profanity_result = await self._check_profanity(message)
                if profanity_result['contains_profanity']:
                    await self._take_action(update, context, 'profanity', f"كلمات غير مناسبة: {', '.join(profanity_result['detected_words'])}")
                    return False
            
            # فحص الروابط
            if filter_settings.get('filter_links', True):
                if await self._check_links(message):
                    await self._take_action(update, context, 'links', 'رابط غير مسموح')
                    return False
            
            # فحص الوسائط
            if await self._check_media_filters(message, filter_settings):
                await self._take_action(update, context, 'media', 'وسائط غير مسموحة')
                return False
            
            # حفظ الرسالة في قاعدة البيانات
            await self._save_message(message)
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تصفية الرسالة: {e}")
            return True  # السماح بالرسالة في حالة الخطأ
    
    async def _check_flood_protection(self, message: Message) -> bool:
        """فحص حماية الفيضان"""
        try:
            user_id = message.from_user.id
            chat_id = message.chat_id
            current_time = datetime.now(timezone.utc)
            
            # إنشاء مفتاح فريد للمستخدم والمجموعة
            key = f"{user_id}_{chat_id}"
            
            if key not in self.flood_protection:
                self.flood_protection[key] = []
            
            # إضافة الوقت الحالي
            self.flood_protection[key].append(current_time)
            
            # إزالة الأوقات القديمة (أكثر من دقيقة)
            cutoff_time = current_time - timedelta(minutes=1)
            self.flood_protection[key] = [
                t for t in self.flood_protection[key] if t > cutoff_time
            ]
            
            # فحص عدد الرسائل في الدقيقة الواحدة
            messages_per_minute = len(self.flood_protection[key])
            max_messages = settings.RATE_LIMIT_MESSAGES_PER_MINUTE
            
            return messages_per_minute > max_messages
            
        except Exception as e:
            logger.error(f"خطأ في فحص حماية الفيضان: {e}")
            return False
    
    async def _check_spam(self, message: Message) -> Dict[str, Any]:
        """فحص الرسائل المزعجة"""
        try:
            text = message.text or message.caption or ""
            
            # استخدام Gemini AI لكشف الرسائل المزعجة
            spam_result = await gemini_client.detect_spam(text)
            
            # فحوصات إضافية محلية
            local_checks = []
            
            # فحص التكرار المفرط للأحرف
            if re.search(r'(.)\1{4,}', text):
                local_checks.append("تكرار مفرط للأحرف")
            
            # فحص الأحرف الخاصة المفرطة
            special_chars = len(re.findall(r'[!@#$%^&*()_+=\[\]{}|;:,.<>?]', text))
            if special_chars > len(text) * 0.3:
                local_checks.append("أحرف خاصة مفرطة")
            
            # فحص الأرقام المفرطة
            numbers = len(re.findall(r'\d', text))
            if numbers > len(text) * 0.5:
                local_checks.append("أرقام مفرطة")
            
            # فحص الروابط المتعددة
            links = len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text))
            if links > 2:
                local_checks.append("روابط متعددة")
            
            # دمج النتائج
            if local_checks:
                spam_result['is_spam'] = True
                spam_result['reasons'].extend(local_checks)
                spam_result['confidence'] = max(spam_result['confidence'], 0.8)
            
            return spam_result
            
        except Exception as e:
            logger.error(f"خطأ في فحص الرسائل المزعجة: {e}")
            return {
                "is_spam": False,
                "confidence": 0.0,
                "reasons": [],
                "category": "normal"
            }
    
    async def _check_profanity(self, message: Message) -> Dict[str, Any]:
        """فحص الكلمات النابية"""
        try:
            text = message.text or message.caption or ""
            
            # استخدام Gemini AI لفحص الكلمات النابية
            profanity_result = await gemini_client.check_profanity(text)
            
            # فحص محلي للكلمات المحظورة
            chat_id = message.chat_id
            group = group_repo.get_group_by_id(chat_id)
            
            banned_words = []
            if group and group.banned_words:
                banned_words.extend(group.banned_words)
            
            # إضافة الكلمات المحظورة الافتراضية
            language = group.language if group else 'ar'
            if language in self.default_banned_words:
                banned_words.extend(self.default_banned_words[language])
            
            # فحص النص للكلمات المحظورة
            text_lower = text.lower()
            detected_local = []
            for word in banned_words:
                if word.lower() in text_lower:
                    detected_local.append(word)
            
            # دمج النتائج
            if detected_local:
                profanity_result['contains_profanity'] = True
                profanity_result['detected_words'].extend(detected_local)
                profanity_result['confidence'] = max(profanity_result['confidence'], 0.9)
            
            return profanity_result
            
        except Exception as e:
            logger.error(f"خطأ في فحص الكلمات النابية: {e}")
            return {
                "contains_profanity": False,
                "confidence": 0.0,
                "detected_words": [],
                "severity": "low"
            }
    
    async def _check_links(self, message: Message) -> bool:
        """فحص الروابط"""
        try:
            text = message.text or message.caption or ""
            
            # البحث عن الروابط
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            urls = re.findall(url_pattern, text)
            
            # فحص الأنماط المشبوهة
            for pattern in self.suspicious_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return True
            
            # فحص النطاقات المشبوهة
            for url in urls:
                try:
                    parsed = urlparse(url)
                    domain = parsed.netloc.lower()
                    if domain in self.suspicious_domains:
                        return True
                except:
                    continue
            
            # فحص الروابط المختصرة
            short_url_patterns = [
                r'bit\.ly', r'tinyurl\.com', r'goo\.gl', r'ow\.ly',
                r't\.co', r'short\.link', r'tiny\.cc'
            ]
            
            for pattern in short_url_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في فحص الروابط: {e}")
            return False
    
    async def _check_media_filters(self, message: Message, filter_settings: Dict[str, Any]) -> bool:
        """فحص مرشحات الوسائط"""
        try:
            # فحص الصور
            if filter_settings.get('filter_media', False) and message.photo:
                return True
            
            # فحص الفيديوهات
            if filter_settings.get('filter_media', False) and message.video:
                return True
            
            # فحص الملصقات
            if filter_settings.get('filter_stickers', False) and message.sticker:
                return True
            
            # فحص الرسائل الصوتية
            if filter_settings.get('filter_voice', False) and message.voice:
                return True
            
            # فحص الملفات
            if filter_settings.get('filter_documents', False) and message.document:
                return True
            
            # فحص الرسائل الصوتية (Audio)
            if filter_settings.get('filter_voice', False) and message.audio:
                return True
            
            # فحص الرسوم المتحركة (GIF)
            if filter_settings.get('filter_media', False) and message.animation:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في فحص مرشحات الوسائط: {e}")
            return False
    
    async def _take_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE, violation_type: str, reason: str):
        """اتخاذ إجراء ضد المخالفة"""
        try:
            message = update.message
            chat_id = message.chat_id
            user_id = message.from_user.id
            
            # حذف الرسالة
            await context.bot.delete_message(chat_id, message.message_id)
            
            # تسجيل الإجراء
            with db_manager.get_session() as session:
                action = Action(
                    group_id=chat_id,
                    performed_by_id=context.bot.id,  # البوت نفسه
                    target_user_id=user_id,
                    action_type=ActionType.DELETE_MESSAGE,
                    reason=f"{violation_type}: {reason}",
                    additional_data={'message_id': message.message_id}
                )
                session.add(action)
                session.commit()
            
            # إرسال تحذير للمستخدم (رسالة خاصة)
            try:
                warning_message = f"""
⚠️ **تحذير**

تم حذف رسالتك في {message.chat.title} لأنها تحتوي على: {reason}

يرجى مراجعة قواعد المجموعة والالتزام بها.
                """
                
                await context.bot.send_message(
                    chat_id=user_id,
                    text=warning_message,
                    parse_mode='Markdown'
                )
            except:
                # إذا فشل إرسال الرسالة الخاصة، إرسال تحذير في المجموعة
                warning_message = f"⚠️ {message.from_user.first_name}، تم حذف رسالتك لمخالفة قواعد المجموعة."
                warning_msg = await context.bot.send_message(
                    chat_id=chat_id,
                    text=warning_message,
                    reply_to_message_id=message.message_id if message else None
                )
                
                # حذف رسالة التحذير بعد 10 ثوانٍ
                context.job_queue.run_once(
                    lambda context: context.bot.delete_message(chat_id, warning_msg.message_id),
                    when=10
                )
            
            # زيادة عدد التحذيرات للمستخدم
            await self._increment_user_warnings(user_id, chat_id)
            
            logger.info(f"تم اتخاذ إجراء ضد المستخدم {user_id} في المجموعة {chat_id}: {violation_type}")
            
        except Exception as e:
            logger.error(f"خطأ في اتخاذ إجراء ضد المخالفة: {e}")
    
    async def _increment_user_warnings(self, user_id: int, chat_id: int):
        """زيادة عدد تحذيرات المستخدم"""
        try:
            from ..database.database import member_repo
            
            member = member_repo.get_member(user_id, chat_id)
            if member:
                with db_manager.get_session() as session:
                    member = session.merge(member)
                    member.warnings += 1
                    
                    # إجراءات تلقائية بناءً على عدد التحذيرات
                    if member.warnings >= 5:
                        # حظر مؤقت لمدة ساعة
                        member.is_muted = True
                        member.mute_until = datetime.now(timezone.utc) + timedelta(hours=1)
                    elif member.warnings >= 10:
                        # حظر دائم
                        member.is_banned = True
                    
                    session.commit()
            
        except Exception as e:
            logger.error(f"خطأ في زيادة تحذيرات المستخدم: {e}")
    
    async def _save_message(self, message: Message):
        """حفظ الرسالة في قاعدة البيانات"""
        try:
            # تحديد نوع الرسالة
            message_type = DBMessageType.TEXT
            file_id = None
            file_size = None
            
            if message.photo:
                message_type = DBMessageType.PHOTO
                file_id = message.photo[-1].file_id
                file_size = message.photo[-1].file_size
            elif message.video:
                message_type = DBMessageType.VIDEO
                file_id = message.video.file_id
                file_size = message.video.file_size
            elif message.audio:
                message_type = DBMessageType.AUDIO
                file_id = message.audio.file_id
                file_size = message.audio.file_size
            elif message.voice:
                message_type = DBMessageType.VOICE
                file_id = message.voice.file_id
                file_size = message.voice.file_size
            elif message.document:
                message_type = DBMessageType.DOCUMENT
                file_id = message.document.file_id
                file_size = message.document.file_size
            elif message.sticker:
                message_type = DBMessageType.STICKER
                file_id = message.sticker.file_id
                file_size = message.sticker.file_size
            elif message.animation:
                message_type = DBMessageType.ANIMATION
                file_id = message.animation.file_id
                file_size = message.animation.file_size
            
            # تحليل المشاعر للنصوص
            sentiment_score = None
            language_detected = None
            
            text = message.text or message.caption
            if text:
                # كشف اللغة
                language_detected = await gemini_client.detect_language(text)
                
                # تحليل المشاعر
                sentiment_result = await gemini_client.analyze_sentiment(text)
                if sentiment_result['sentiment'] == 'positive':
                    sentiment_score = sentiment_result['confidence']
                elif sentiment_result['sentiment'] == 'negative':
                    sentiment_score = -sentiment_result['confidence']
                else:
                    sentiment_score = 0.0
            
            # حفظ الرسالة
            message_data = {
                'message_id': message.message_id,
                'user_id': message.from_user.id,
                'group_id': message.chat_id,
                'text': text,
                'message_type': message_type,
                'file_id': file_id,
                'file_size': file_size,
                'sentiment_score': sentiment_score,
                'language_detected': language_detected,
                'reply_to_message_id': message.reply_to_message.message_id if message.reply_to_message else None,
                'forward_from_user_id': message.forward_from.id if message.forward_from else None,
                'forward_from_chat_id': message.forward_from_chat.id if message.forward_from_chat else None
            }
            
            message_repo.save_message(message_data)
            
        except Exception as e:
            logger.error(f"خطأ في حفظ الرسالة: {e}")
    
    async def _is_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
        """التحقق من كون المستخدم مشرف"""
        try:
            chat_id = update.effective_chat.id
            member = await context.bot.get_chat_member(chat_id, user_id)
            
            from telegram.constants import ChatMemberStatus
            return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من صلاحيات المشرف: {e}")
            return False
    
    async def add_banned_word(self, chat_id: int, word: str):
        """إضافة كلمة محظورة"""
        try:
            group = group_repo.get_group_by_id(chat_id)
            if group:
                banned_words = group.banned_words or []
                if word not in banned_words:
                    banned_words.append(word)
                    group_repo.update_group_settings(chat_id, {'banned_words': banned_words})
                    return True
            return False
            
        except Exception as e:
            logger.error(f"خطأ في إضافة كلمة محظورة: {e}")
            return False
    
    async def remove_banned_word(self, chat_id: int, word: str):
        """إزالة كلمة محظورة"""
        try:
            group = group_repo.get_group_by_id(chat_id)
            if group and group.banned_words:
                banned_words = group.banned_words
                if word in banned_words:
                    banned_words.remove(word)
                    group_repo.update_group_settings(chat_id, {'banned_words': banned_words})
                    return True
            return False
            
        except Exception as e:
            logger.error(f"خطأ في إزالة كلمة محظورة: {e}")
            return False
    
    async def get_banned_words(self, chat_id: int) -> List[str]:
        """الحصول على قائمة الكلمات المحظورة"""
        try:
            group = group_repo.get_group_by_id(chat_id)
            if group and group.banned_words:
                return group.banned_words
            return []
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على الكلمات المحظورة: {e}")
            return []

# إنشاء مثيل مرشح المحتوى
content_filter = ContentFilter()

