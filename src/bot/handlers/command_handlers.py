"""
معالجات الأوامر لبوت تيليجرام تيكنو
"""
import logging
from datetime import datetime, timezone
from typing import Optional, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatType

from ..database.database import user_repo, group_repo, member_repo
from ..modules.member_management import member_manager
from ..modules.content_filtering import content_filter
from ..ai_integration.gemini_client import gemini_client
from ..config.settings import settings

logger = logging.getLogger(__name__)

class CommandHandlers:
    """معالجات الأوامر"""
    
    def __init__(self):
        """تهيئة معالجات الأوامر"""
        pass
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /start"""
        try:
            user = update.effective_user
            chat = update.effective_chat
            
            # حفظ/تحديث معلومات المستخدم
            user_data = {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'language_code': user.language_code or 'ar',
                'is_bot': user.is_bot
            }
            user_repo.create_or_update_user(user_data)
            
            if chat.type == ChatType.PRIVATE:
                # رسالة ترحيب في المحادثة الخاصة
                welcome_text = f"""
🤖 **مرحباً {user.first_name}!**

أنا **تيكنو**، بوت إدارة المجموعات المتقدم! 🚀

**ما يمكنني فعله:**
• 👥 إدارة الأعضاء والمشرفين
• 🛡️ تصفية المحتوى ومكافحة السبام
• 🤖 ردود ذكية باستخدام الذكاء الاصطناعي
• 📊 إحصائيات وتقارير مفصلة
• ⚙️ واجهة إدارة متقدمة
• 🌍 دعم متعدد اللغات
• 📅 رسائل مجدولة واستبيانات
• 🔧 أوامر مخصصة وميزات متقدمة

**للبدء:**
1. أضفني إلى مجموعتك
2. امنحني صلاحيات المشرف
3. استخدم /setup لإعداد البوت

**الأوامر الأساسية:**
/help - عرض المساعدة
/settings - الإعدادات
/stats - الإحصائيات

**الدعم:** @techno_support
**القناة:** @techno_updates
                """
                
                keyboard = [
                    [InlineKeyboardButton("📚 دليل الاستخدام", url="https://t.me/techno_guide")],
                    [InlineKeyboardButton("💬 الدعم", url="https://t.me/techno_support"),
                     InlineKeyboardButton("📢 التحديثات", url="https://t.me/techno_updates")],
                    [InlineKeyboardButton("➕ إضافة إلى مجموعة", url=f"https://t.me/{context.bot.username}?startgroup=true")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    welcome_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            else:
                # رسالة في المجموعة
                # حفظ/تحديث معلومات المجموعة
                group_data = {
                    'id': chat.id,
                    'title': chat.title,
                    'username': chat.username,
                    'type': chat.type,
                    'description': chat.description
                }
                group_repo.create_or_update_group(group_data)
                
                # إضافة العضو إلى المجموعة
                member_repo.add_member(user.id, chat.id)
                
                welcome_text = f"""
🎉 **مرحباً! أنا تيكنو** 🤖

تم تفعيلي بنجاح في **{chat.title}**!

استخدم /setup لإعداد البوت
استخدم /help لعرض جميع الأوامر

**ميزات سريعة:**
• حماية تلقائية من السبام ✅
• ترحيب ذكي بالأعضاء الجدد 👋
• تصفية المحتوى المتقدمة 🛡️
• ردود ذكية بالذكاء الاصطناعي 🧠
                """
                
                keyboard = [
                    [InlineKeyboardButton("⚙️ الإعدادات", callback_data="admin_settings")],
                    [InlineKeyboardButton("📊 الإحصائيات", callback_data="group_stats"),
                     InlineKeyboardButton("❓ المساعدة", callback_data="help_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    welcome_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
        except Exception as e:
            logger.error(f"خطأ في معالج أمر /start: {e}")
            await update.message.reply_text("❌ حدث خطأ أثناء تشغيل الأمر.")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /help"""
        try:
            chat = update.effective_chat
            user_id = update.effective_user.id
            
            # التحقق من صلاحيات المستخدم
            is_admin = False
            if chat.type != ChatType.PRIVATE:
                is_admin = await self._is_admin(update, context, user_id)
            
            # أوامر عامة
            general_commands = """
**🔧 الأوامر العامة:**
/start - بدء البوت
/help - عرض المساعدة
/info - معلومات البوت
/stats - إحصائيات المجموعة
/rules - قواعد المجموعة
/report - الإبلاغ عن مشكلة
            """
            
            # أوامر المشرفين
            admin_commands = """
**👑 أوامر المشرفين:**
/setup - إعداد البوت
/settings - إعدادات المجموعة
/ban - حظر عضو
/unban - إلغاء حظر عضو
/mute - كتم عضو
/unmute - إلغاء كتم عضو
/kick - طرد عضو
/warn - تحذير عضو
/promote - ترقية عضو
/demote - تخفيض رتبة عضو
/purge - حذف رسائل
/lock - قفل ميزة
/unlock - إلغاء قفل ميزة
/welcome - تعديل رسالة الترحيب
/setrules - تعديل قواعد المجموعة
/addword - إضافة كلمة محظورة
/delword - حذف كلمة محظورة
/filter - إضافة مرشح
/unfilter - حذف مرشح
/backup - نسخ احتياطي
/restore - استعادة نسخة احتياطية
            """
            
            # أوامر الذكاء الاصطناعي
            ai_commands = """
**🤖 أوامر الذكاء الاصطناعي:**
/ask - طرح سؤال
/summarize - تلخيص المحادثة
/translate - ترجمة نص
/sentiment - تحليل المشاعر
/suggest - اقتراح محتوى
/resolve - المساعدة في حل نزاع
            """
            
            # أوامر الميزات المتقدمة
            advanced_commands = """
**⚡ الميزات المتقدمة:**
/schedule - جدولة رسالة
/poll - إنشاء استبيان
/quiz - إنشاء اختبار
/timer - تعيين مؤقت
/remind - تذكير
/note - حفظ ملاحظة
/getnote - استرجاع ملاحظة
/connect - ربط قناة
/disconnect - إلغاء ربط قناة
/export - تصدير البيانات
/import - استيراد البيانات
            """
            
            help_text = general_commands
            
            if is_admin:
                help_text += admin_commands + ai_commands + advanced_commands
            else:
                help_text += "\n**💡 ملاحظة:** بعض الأوامر متاحة للمشرفين فقط."
            
            help_text += f"""

**🔗 روابط مفيدة:**
• [دليل الاستخدام الكامل](https://t.me/techno_guide)
• [قناة التحديثات](https://t.me/techno_updates)
• [مجموعة الدعم](https://t.me/techno_support)

**📱 الإصدار:** 1.0.0
**👨‍💻 المطور:** @techno_dev
            """
            
            keyboard = [
                [InlineKeyboardButton("⚙️ الإعدادات", callback_data="admin_settings")],
                [InlineKeyboardButton("📊 الإحصائيات", callback_data="group_stats"),
                 InlineKeyboardButton("🔧 الميزات", callback_data="features_menu")],
                [InlineKeyboardButton("💬 الدعم", url="https://t.me/techno_support")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                help_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"خطأ في معالج أمر /help: {e}")
            await update.message.reply_text("❌ حدث خطأ أثناء عرض المساعدة.")
    
    async def setup_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /setup"""
        try:
            chat = update.effective_chat
            user_id = update.effective_user.id
            
            # التحقق من أن الأمر في مجموعة
            if chat.type == ChatType.PRIVATE:
                await update.message.reply_text("❌ هذا الأمر يعمل في المجموعات فقط.")
                return
            
            # التحقق من صلاحيات المشرف
            if not await self._is_admin(update, context, user_id):
                await update.message.reply_text("❌ هذا الأمر متاح للمشرفين فقط.")
                return
            
            # إعداد المجموعة
            setup_text = f"""
🔧 **إعداد البوت في {chat.title}**

مرحباً! دعني أساعدك في إعداد البوت بشكل مثالي.

**الخطوات:**
1️⃣ تأكد من منح البوت صلاحيات المشرف
2️⃣ اختر الميزات التي تريد تفعيلها
3️⃣ قم بتخصيص الإعدادات حسب احتياجاتك

**الميزات المتاحة:**
✅ إدارة الأعضاء
✅ تصفية المحتوى
✅ الذكاء الاصطناعي
✅ الإحصائيات والتقارير
✅ الرسائل المجدولة
✅ الاستبيانات والاختبارات

اختر من القائمة أدناه:
            """
            
            keyboard = [
                [InlineKeyboardButton("🛡️ إعدادات الحماية", callback_data="setup_protection")],
                [InlineKeyboardButton("👥 إعدادات الأعضاء", callback_data="setup_members")],
                [InlineKeyboardButton("🤖 إعدادات الذكاء الاصطناعي", callback_data="setup_ai")],
                [InlineKeyboardButton("📊 إعدادات الإحصائيات", callback_data="setup_analytics")],
                [InlineKeyboardButton("🌍 إعدادات اللغة", callback_data="setup_language")],
                [InlineKeyboardButton("✅ إنهاء الإعداد", callback_data="setup_complete")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                setup_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"خطأ في معالج أمر /setup: {e}")
            await update.message.reply_text("❌ حدث خطأ أثناء الإعداد.")
    
    async def ban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /ban"""
        try:
            # التحقق من الصلاحيات
            if not await self._is_admin(update, context, update.effective_user.id):
                await update.message.reply_text("❌ هذا الأمر متاح للمشرفين فقط.")
                return
            
            # تحليل الأمر
            args = context.args
            target_user_id = None
            reason = None
            duration = None
            
            # إذا كان الأمر رد على رسالة
            if update.message.reply_to_message:
                target_user_id = update.message.reply_to_message.from_user.id
                if args:
                    # البحث عن المدة والسبب
                    for arg in args:
                        if arg.isdigit():
                            duration = int(arg)
                        else:
                            reason = reason + " " + arg if reason else arg
            elif args:
                # محاولة استخراج معرف المستخدم من الأرجومنت الأول
                try:
                    if args[0].startswith('@'):
                        # البحث عن المستخدم بالاسم
                        username = args[0][1:]
                        # هنا يمكن إضافة منطق البحث عن المستخدم
                    else:
                        target_user_id = int(args[0])
                    
                    # باقي الأرجومنتات للسبب والمدة
                    for arg in args[1:]:
                        if arg.isdigit():
                            duration = int(arg)
                        else:
                            reason = reason + " " + arg if reason else arg
                except ValueError:
                    await update.message.reply_text("❌ معرف المستخدم غير صحيح.")
                    return
            else:
                await update.message.reply_text(
                    "❌ الاستخدام: /ban [معرف المستخدم أو الرد على رسالة] [المدة بالدقائق] [السبب]"
                )
                return
            
            if target_user_id:
                await member_manager.ban_member(update, context, target_user_id, reason, duration)
            else:
                await update.message.reply_text("❌ لم يتم العثور على المستخدم المحدد.")
                
        except Exception as e:
            logger.error(f"خطأ في معالج أمر /ban: {e}")
            await update.message.reply_text("❌ حدث خطأ أثناء تنفيذ الأمر.")
    
    async def unban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /unban"""
        try:
            # التحقق من الصلاحيات
            if not await self._is_admin(update, context, update.effective_user.id):
                await update.message.reply_text("❌ هذا الأمر متاح للمشرفين فقط.")
                return
            
            # تحليل الأمر
            args = context.args
            target_user_id = None
            
            if args:
                try:
                    target_user_id = int(args[0])
                except ValueError:
                    await update.message.reply_text("❌ معرف المستخدم غير صحيح.")
                    return
            else:
                await update.message.reply_text("❌ الاستخدام: /unban [معرف المستخدم]")
                return
            
            await member_manager.unban_member(update, context, target_user_id)
                
        except Exception as e:
            logger.error(f"خطأ في معالج أمر /unban: {e}")
            await update.message.reply_text("❌ حدث خطأ أثناء تنفيذ الأمر.")
    
    async def mute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /mute"""
        try:
            # التحقق من الصلاحيات
            if not await self._is_admin(update, context, update.effective_user.id):
                await update.message.reply_text("❌ هذا الأمر متاح للمشرفين فقط.")
                return
            
            # تحليل الأمر
            args = context.args
            target_user_id = None
            duration = None
            
            # إذا كان الأمر رد على رسالة
            if update.message.reply_to_message:
                target_user_id = update.message.reply_to_message.from_user.id
                if args and args[0].isdigit():
                    duration = int(args[0])
            elif args:
                try:
                    target_user_id = int(args[0])
                    if len(args) > 1 and args[1].isdigit():
                        duration = int(args[1])
                except ValueError:
                    await update.message.reply_text("❌ معرف المستخدم غير صحيح.")
                    return
            else:
                await update.message.reply_text(
                    "❌ الاستخدام: /mute [معرف المستخدم أو الرد على رسالة] [المدة بالدقائق]"
                )
                return
            
            if target_user_id:
                await member_manager.mute_member(update, context, target_user_id, duration)
            else:
                await update.message.reply_text("❌ لم يتم العثور على المستخدم المحدد.")
                
        except Exception as e:
            logger.error(f"خطأ في معالج أمر /mute: {e}")
            await update.message.reply_text("❌ حدث خطأ أثناء تنفيذ الأمر.")
    
    async def unmute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /unmute"""
        try:
            # التحقق من الصلاحيات
            if not await self._is_admin(update, context, update.effective_user.id):
                await update.message.reply_text("❌ هذا الأمر متاح للمشرفين فقط.")
                return
            
            # تحليل الأمر
            args = context.args
            target_user_id = None
            
            # إذا كان الأمر رد على رسالة
            if update.message.reply_to_message:
                target_user_id = update.message.reply_to_message.from_user.id
            elif args:
                try:
                    target_user_id = int(args[0])
                except ValueError:
                    await update.message.reply_text("❌ معرف المستخدم غير صحيح.")
                    return
            else:
                await update.message.reply_text(
                    "❌ الاستخدام: /unmute [معرف المستخدم أو الرد على رسالة]"
                )
                return
            
            if target_user_id:
                await member_manager.unmute_member(update, context, target_user_id)
            else:
                await update.message.reply_text("❌ لم يتم العثور على المستخدم المحدد.")
                
        except Exception as e:
            logger.error(f"خطأ في معالج أمر /unmute: {e}")
            await update.message.reply_text("❌ حدث خطأ أثناء تنفيذ الأمر.")
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /stats"""
        try:
            chat = update.effective_chat
            
            if chat.type == ChatType.PRIVATE:
                await update.message.reply_text("❌ هذا الأمر يعمل في المجموعات فقط.")
                return
            
            await member_manager.get_member_stats(update, context)
                
        except Exception as e:
            logger.error(f"خطأ في معالج أمر /stats: {e}")
            await update.message.reply_text("❌ حدث خطأ أثناء جلب الإحصائيات.")
    
    async def ask_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /ask - طرح سؤال للذكاء الاصطناعي"""
        try:
            args = context.args
            if not args:
                await update.message.reply_text("❌ الاستخدام: /ask [سؤالك هنا]")
                return
            
            question = " ".join(args)
            
            # إرسال رسالة "يكتب..."
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            # الحصول على الرد من Gemini AI
            response = await gemini_client.generate_response(question)
            
            if response:
                await update.message.reply_text(
                    f"🤖 **الجواب:**\n\n{response}",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("❌ عذراً، لم أتمكن من الإجابة على سؤالك.")
                
        except Exception as e:
            logger.error(f"خطأ في معالج أمر /ask: {e}")
            await update.message.reply_text("❌ حدث خطأ أثناء معالجة السؤال.")
    
    async def summarize_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /summarize - تلخيص المحادثة"""
        try:
            chat_id = update.effective_chat.id
            
            # الحصول على الرسائل الحديثة
            recent_messages = message_repo.get_recent_messages(chat_id, 20)
            
            if not recent_messages:
                await update.message.reply_text("❌ لا توجد رسائل كافية للتلخيص.")
                return
            
            # تحويل الرسائل إلى نصوص
            message_texts = []
            for msg in recent_messages:
                if msg.text:
                    user = user_repo.get_user_by_id(msg.user_id)
                    user_name = user.first_name if user else "مستخدم"
                    message_texts.append(f"{user_name}: {msg.text}")
            
            if not message_texts:
                await update.message.reply_text("❌ لا توجد رسائل نصية للتلخيص.")
                return
            
            # إرسال رسالة "يكتب..."
            await context.bot.send_chat_action(chat_id=chat_id, action="typing")
            
            # تلخيص المحادثة
            summary = await gemini_client.summarize_conversation(message_texts)
            
            if summary:
                await update.message.reply_text(
                    f"📝 **ملخص المحادثة:**\n\n{summary}",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("❌ لم أتمكن من تلخيص المحادثة.")
                
        except Exception as e:
            logger.error(f"خطأ في معالج أمر /summarize: {e}")
            await update.message.reply_text("❌ حدث خطأ أثناء تلخيص المحادثة.")
    
    async def addword_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /addword - إضافة كلمة محظورة"""
        try:
            # التحقق من الصلاحيات
            if not await self._is_admin(update, context, update.effective_user.id):
                await update.message.reply_text("❌ هذا الأمر متاح للمشرفين فقط.")
                return
            
            args = context.args
            if not args:
                await update.message.reply_text("❌ الاستخدام: /addword [الكلمة المحظورة]")
                return
            
            word = " ".join(args)
            chat_id = update.effective_chat.id
            
            success = await content_filter.add_banned_word(chat_id, word)
            
            if success:
                await update.message.reply_text(f"✅ تم إضافة الكلمة '{word}' إلى قائمة الكلمات المحظورة.")
            else:
                await update.message.reply_text("❌ فشل في إضافة الكلمة.")
                
        except Exception as e:
            logger.error(f"خطأ في معالج أمر /addword: {e}")
            await update.message.reply_text("❌ حدث خطأ أثناء إضافة الكلمة.")
    
    async def delword_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /delword - حذف كلمة محظورة"""
        try:
            # التحقق من الصلاحيات
            if not await self._is_admin(update, context, update.effective_user.id):
                await update.message.reply_text("❌ هذا الأمر متاح للمشرفين فقط.")
                return
            
            args = context.args
            if not args:
                await update.message.reply_text("❌ الاستخدام: /delword [الكلمة المحظورة]")
                return
            
            word = " ".join(args)
            chat_id = update.effective_chat.id
            
            success = await content_filter.remove_banned_word(chat_id, word)
            
            if success:
                await update.message.reply_text(f"✅ تم حذف الكلمة '{word}' من قائمة الكلمات المحظورة.")
            else:
                await update.message.reply_text("❌ الكلمة غير موجودة في القائمة.")
                
        except Exception as e:
            logger.error(f"خطأ في معالج أمر /delword: {e}")
            await update.message.reply_text("❌ حدث خطأ أثناء حذف الكلمة.")
    
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

# إنشاء مثيل معالجات الأوامر
command_handlers = CommandHandlers()

