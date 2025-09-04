"""
واجهة الإدارة لبوت تيليجرام تيكنو
"""
import logging
from typing import Dict, Any, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ContextTypes

from ..database.database import group_repo, user_repo, member_repo
from ..config.settings import settings

logger = logging.getLogger(__name__)

class AdminPanel:
    """لوحة الإدارة"""
    
    def __init__(self):
        """تهيئة لوحة الإدارة"""
        self.menu_stack = {}  # لتتبع مسار القوائم لكل مستخدم
    
    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض القائمة الرئيسية للإدارة"""
        try:
            query = update.callback_query
            if query:
                await query.answer()
            
            chat_id = update.effective_chat.id
            user_id = update.effective_user.id
            
            # التحقق من صلاحيات المشرف
            if not await self._is_admin(update, context, user_id):
                if query:
                    await query.edit_message_text("❌ هذه الواجهة متاحة للمشرفين فقط.")
                else:
                    await update.message.reply_text("❌ هذه الواجهة متاحة للمشرفين فقط.")
                return
            
            # الحصول على معلومات المجموعة
            group = group_repo.get_group_by_id(chat_id)
            group_name = group.title if group else "المجموعة"
            
            main_menu_text = f"""
🎛️ **لوحة إدارة تيكنو**
📍 المجموعة: {group_name}

مرحباً بك في لوحة الإدارة المتقدمة! 
يمكنك من هنا إدارة جميع جوانب البوت بسهولة.

اختر القسم الذي تريد إدارته:
            """
            
            keyboard = [
                [InlineKeyboardButton("👥 إدارة الأعضاء", callback_data="admin_members"),
                 InlineKeyboardButton("🛡️ إعدادات الحماية", callback_data="admin_protection")],
                [InlineKeyboardButton("🤖 الذكاء الاصطناعي", callback_data="admin_ai"),
                 InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_analytics")],
                [InlineKeyboardButton("⚙️ الإعدادات العامة", callback_data="admin_general"),
                 InlineKeyboardButton("🔧 الميزات المتقدمة", callback_data="admin_advanced")],
                [InlineKeyboardButton("📝 الرسائل والمحتوى", callback_data="admin_content"),
                 InlineKeyboardButton("🌍 اللغة والتوطين", callback_data="admin_language")],
                [InlineKeyboardButton("💾 النسخ الاحتياطي", callback_data="admin_backup"),
                 InlineKeyboardButton("📋 السجلات", callback_data="admin_logs")],
                [InlineKeyboardButton("❓ المساعدة", callback_data="admin_help"),
                 InlineKeyboardButton("🔄 تحديث", callback_data="admin_settings")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if query:
                await query.edit_message_text(
                    main_menu_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(
                    main_menu_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
        except Exception as e:
            logger.error(f"خطأ في عرض القائمة الرئيسية: {e}")
    
    async def show_members_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة إدارة الأعضاء"""
        try:
            query = update.callback_query
            await query.answer()
            
            chat_id = update.effective_chat.id
            
            # الحصول على إحصائيات الأعضاء
            members = member_repo.get_group_members(chat_id)
            total_members = len(members)
            
            members_menu_text = f"""
👥 **إدارة الأعضاء**

📊 **الإحصائيات السريعة:**
• إجمالي الأعضاء: {total_members}
• الأعضاء النشطون: {len([m for m in members if m.last_activity])}
• المحظورون: {len([m for m in members if m.is_banned])}
• المكتومون: {len([m for m in members if m.is_muted])}

اختر الإجراء المطلوب:
            """
            
            keyboard = [
                [InlineKeyboardButton("📋 قائمة الأعضاء", callback_data="members_list"),
                 InlineKeyboardButton("👑 المشرفون", callback_data="members_admins")],
                [InlineKeyboardButton("🚫 المحظورون", callback_data="members_banned"),
                 InlineKeyboardButton("🔇 المكتومون", callback_data="members_muted")],
                [InlineKeyboardButton("⚠️ التحذيرات", callback_data="members_warnings"),
                 InlineKeyboardButton("🏆 النقاط والمكافآت", callback_data="members_points")],
                [InlineKeyboardButton("🔍 البحث عن عضو", callback_data="members_search"),
                 InlineKeyboardButton("📊 إحصائيات مفصلة", callback_data="members_detailed_stats")],
                [InlineKeyboardButton("🧹 تنظيف الأعضاء", callback_data="members_cleanup"),
                 InlineKeyboardButton("📤 تصدير قائمة", callback_data="members_export")],
                [InlineKeyboardButton("🔙 العودة", callback_data="admin_settings")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                members_menu_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"خطأ في عرض قائمة إدارة الأعضاء: {e}")
    
    async def show_protection_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة إعدادات الحماية"""
        try:
            query = update.callback_query
            await query.answer()
            
            chat_id = update.effective_chat.id
            group_settings = group_repo.get_group_settings(chat_id)
            filter_settings = group_settings.get('filter_settings', settings.DEFAULT_FILTER_SETTINGS)
            
            # رموز الحالة
            def status_icon(enabled):
                return "✅" if enabled else "❌"
            
            protection_menu_text = f"""
🛡️ **إعدادات الحماية**

**حالة المرشحات الحالية:**
{status_icon(filter_settings.get('anti_spam', True))} مكافحة السبام
{status_icon(filter_settings.get('profanity_filter', True))} فلترة الكلمات النابية
{status_icon(filter_settings.get('filter_links', True))} فلترة الروابط
{status_icon(filter_settings.get('filter_media', False))} فلترة الوسائط
{status_icon(filter_settings.get('flood_protection', True))} حماية من الفيضان
{status_icon(filter_settings.get('filter_stickers', False))} فلترة الملصقات

اختر الإعداد المطلوب تعديله:
            """
            
            keyboard = [
                [InlineKeyboardButton(f"{'🔴' if not filter_settings.get('anti_spam', True) else '🟢'} مكافحة السبام", 
                                    callback_data="toggle_anti_spam"),
                 InlineKeyboardButton(f"{'🔴' if not filter_settings.get('profanity_filter', True) else '🟢'} الكلمات النابية", 
                                    callback_data="toggle_profanity")],
                [InlineKeyboardButton(f"{'🔴' if not filter_settings.get('filter_links', True) else '🟢'} فلترة الروابط", 
                                    callback_data="toggle_links"),
                 InlineKeyboardButton(f"{'🔴' if not filter_settings.get('filter_media', False) else '🟢'} فلترة الوسائط", 
                                    callback_data="toggle_media")],
                [InlineKeyboardButton(f"{'🔴' if not filter_settings.get('flood_protection', True) else '🟢'} حماية الفيضان", 
                                    callback_data="toggle_flood"),
                 InlineKeyboardButton(f"{'🔴' if not filter_settings.get('filter_stickers', False) else '🟢'} فلترة الملصقات", 
                                    callback_data="toggle_stickers")],
                [InlineKeyboardButton("📝 الكلمات المحظورة", callback_data="banned_words"),
                 InlineKeyboardButton("🔗 النطاقات المسموحة", callback_data="allowed_domains")],
                [InlineKeyboardButton("⚙️ إعدادات متقدمة", callback_data="protection_advanced"),
                 InlineKeyboardButton("📊 إحصائيات الحماية", callback_data="protection_stats")],
                [InlineKeyboardButton("🔙 العودة", callback_data="admin_settings")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                protection_menu_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"خطأ في عرض قائمة إعدادات الحماية: {e}")
    
    async def show_ai_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة إعدادات الذكاء الاصطناعي"""
        try:
            query = update.callback_query
            await query.answer()
            
            chat_id = update.effective_chat.id
            group_settings = group_repo.get_group_settings(chat_id)
            features = group_settings.get('features_enabled', settings.FEATURES)
            
            def status_icon(enabled):
                return "✅" if enabled else "❌"
            
            ai_menu_text = f"""
🤖 **إعدادات الذكاء الاصطناعي**

**الميزات المفعلة:**
{status_icon(features.get('ai_integration', True))} الذكاء الاصطناعي العام
{status_icon(features.get('auto_responses', True))} الردود التلقائية
{status_icon(features.get('sentiment_analysis', True))} تحليل المشاعر
{status_icon(features.get('content_suggestions', True))} اقتراح المحتوى
{status_icon(features.get('conflict_resolution', True))} حل النزاعات
{status_icon(features.get('smart_moderation', True))} الإشراف الذكي

اختر الإعداد المطلوب:
            """
            
            keyboard = [
                [InlineKeyboardButton(f"{'🔴' if not features.get('ai_integration', True) else '🟢'} الذكاء الاصطناعي", 
                                    callback_data="toggle_ai_integration"),
                 InlineKeyboardButton(f"{'🔴' if not features.get('auto_responses', True) else '🟢'} الردود التلقائية", 
                                    callback_data="toggle_auto_responses")],
                [InlineKeyboardButton(f"{'🔴' if not features.get('sentiment_analysis', True) else '🟢'} تحليل المشاعر", 
                                    callback_data="toggle_sentiment"),
                 InlineKeyboardButton(f"{'🔴' if not features.get('content_suggestions', True) else '🟢'} اقتراح المحتوى", 
                                    callback_data="toggle_suggestions")],
                [InlineKeyboardButton("💬 إدارة الردود التلقائية", callback_data="ai_auto_responses"),
                 InlineKeyboardButton("🎯 كلمات مفتاحية", callback_data="ai_keywords")],
                [InlineKeyboardButton("📊 إحصائيات الذكاء الاصطناعي", callback_data="ai_stats"),
                 InlineKeyboardButton("🔧 إعدادات متقدمة", callback_data="ai_advanced")],
                [InlineKeyboardButton("🔙 العودة", callback_data="admin_settings")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                ai_menu_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"خطأ في عرض قائمة إعدادات الذكاء الاصطناعي: {e}")
    
    async def show_content_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة إدارة الرسائل والمحتوى"""
        try:
            query = update.callback_query
            await query.answer()
            
            content_menu_text = """
📝 **إدارة الرسائل والمحتوى**

قم بتخصيص رسائل البوت والمحتوى التفاعلي:
            """
            
            keyboard = [
                [InlineKeyboardButton("👋 رسالة الترحيب", callback_data="content_welcome"),
                 InlineKeyboardButton("📋 قواعد المجموعة", callback_data="content_rules")],
                [InlineKeyboardButton("🤖 الردود التلقائية", callback_data="content_auto_replies"),
                 InlineKeyboardButton("📅 الرسائل المجدولة", callback_data="content_scheduled")],
                [InlineKeyboardButton("📊 الاستبيانات", callback_data="content_polls"),
                 InlineKeyboardButton("🎯 الاختبارات", callback_data="content_quizzes")],
                [InlineKeyboardButton("📝 الملاحظات", callback_data="content_notes"),
                 InlineKeyboardButton("🔗 الأوامر المخصصة", callback_data="content_commands")],
                [InlineKeyboardButton("🎨 تخصيص الثيمات", callback_data="content_themes"),
                 InlineKeyboardButton("📢 الإعلانات", callback_data="content_announcements")],
                [InlineKeyboardButton("🔙 العودة", callback_data="admin_settings")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                content_menu_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"خطأ في عرض قائمة إدارة المحتوى: {e}")
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الاستعلامات المرتدة"""
        try:
            query = update.callback_query
            data = query.data
            
            # توجيه الاستعلام إلى المعالج المناسب
            if data == "admin_settings":
                await self.show_main_menu(update, context)
            elif data == "admin_members":
                await self.show_members_menu(update, context)
            elif data == "admin_protection":
                await self.show_protection_menu(update, context)
            elif data == "admin_ai":
                await self.show_ai_menu(update, context)
            elif data == "admin_content":
                await self.show_content_menu(update, context)
            elif data.startswith("toggle_"):
                await self.handle_toggle_setting(update, context, data)
            elif data == "group_stats":
                await self.show_group_stats(update, context)
            else:
                await query.answer("هذه الميزة قيد التطوير...")
                
        except Exception as e:
            logger.error(f"خطأ في معالج الاستعلامات المرتدة: {e}")
    
    async def handle_toggle_setting(self, update: Update, context: ContextTypes.DEFAULT_TYPE, setting: str):
        """معالج تبديل الإعدادات"""
        try:
            query = update.callback_query
            await query.answer()
            
            chat_id = update.effective_chat.id
            group_settings = group_repo.get_group_settings(chat_id)
            
            # تحديد نوع الإعداد
            if setting.startswith("toggle_"):
                setting_name = setting.replace("toggle_", "")
                
                # إعدادات الحماية
                protection_settings = ['anti_spam', 'profanity', 'links', 'media', 'flood', 'stickers']
                if setting_name in ['profanity']:
                    setting_name = 'profanity_filter'
                elif setting_name in ['links']:
                    setting_name = 'filter_links'
                elif setting_name in ['media']:
                    setting_name = 'filter_media'
                elif setting_name in ['flood']:
                    setting_name = 'flood_protection'
                elif setting_name in ['stickers']:
                    setting_name = 'filter_stickers'
                
                if setting_name in ['anti_spam', 'profanity_filter', 'filter_links', 'filter_media', 'flood_protection', 'filter_stickers']:
                    # تبديل إعدادات الحماية
                    filter_settings = group_settings.get('filter_settings', settings.DEFAULT_FILTER_SETTINGS)
                    current_value = filter_settings.get(setting_name, True)
                    filter_settings[setting_name] = not current_value
                    
                    group_repo.update_group_settings(chat_id, {'filter_settings': filter_settings})
                    
                    status = "تم تفعيل" if not current_value else "تم إلغاء تفعيل"
                    await query.answer(f"✅ {status} {setting_name}")
                    
                    # إعادة عرض قائمة الحماية
                    await self.show_protection_menu(update, context)
                
                # إعدادات الذكاء الاصطناعي
                elif setting_name in ['ai_integration', 'auto_responses', 'sentiment', 'suggestions']:
                    features = group_settings.get('features_enabled', settings.FEATURES)
                    
                    if setting_name == 'sentiment':
                        setting_name = 'sentiment_analysis'
                    elif setting_name == 'suggestions':
                        setting_name = 'content_suggestions'
                    
                    current_value = features.get(setting_name, True)
                    features[setting_name] = not current_value
                    
                    group_repo.update_group_settings(chat_id, {'features_enabled': features})
                    
                    status = "تم تفعيل" if not current_value else "تم إلغاء تفعيل"
                    await query.answer(f"✅ {status} {setting_name}")
                    
                    # إعادة عرض قائمة الذكاء الاصطناعي
                    await self.show_ai_menu(update, context)
            
        except Exception as e:
            logger.error(f"خطأ في تبديل الإعداد: {e}")
            await query.answer("❌ حدث خطأ أثناء تحديث الإعداد")
    
    async def show_group_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض إحصائيات المجموعة"""
        try:
            query = update.callback_query
            if query:
                await query.answer()
            
            chat_id = update.effective_chat.id
            
            # الحصول على الإحصائيات
            members = member_repo.get_group_members(chat_id)
            total_members = len(members)
            active_members = len([m for m in members if m.last_activity])
            banned_members = len([m for m in members if m.is_banned])
            muted_members = len([m for m in members if m.is_muted])
            
            # إحصائيات الرسائل
            from ..database.database import message_repo
            recent_messages = message_repo.get_recent_messages(chat_id, 100)
            total_messages = len(recent_messages)
            
            stats_text = f"""
📊 **إحصائيات المجموعة**

👥 **الأعضاء:**
• إجمالي الأعضاء: {total_members}
• الأعضاء النشطون: {active_members}
• المحظورون: {banned_members}
• المكتومون: {muted_members}
• معدل النشاط: {(active_members/total_members*100):.1f}%

💬 **الرسائل:**
• الرسائل الحديثة: {total_messages}
• متوسط الرسائل/العضو: {(total_messages/total_members):.1f}

📅 **آخر تحديث:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
            """
            
            keyboard = [
                [InlineKeyboardButton("📈 إحصائيات مفصلة", callback_data="detailed_stats"),
                 InlineKeyboardButton("📊 تقرير شامل", callback_data="full_report")],
                [InlineKeyboardButton("🔄 تحديث", callback_data="group_stats"),
                 InlineKeyboardButton("📤 تصدير", callback_data="export_stats")],
                [InlineKeyboardButton("🔙 العودة", callback_data="admin_settings")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if query:
                await query.edit_message_text(
                    stats_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(
                    stats_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
        except Exception as e:
            logger.error(f"خطأ في عرض إحصائيات المجموعة: {e}")
    
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

# إنشاء مثيل لوحة الإدارة
admin_panel = AdminPanel()

