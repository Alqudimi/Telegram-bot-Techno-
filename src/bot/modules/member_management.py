"""
وحدة إدارة الأعضاء لبوت تيليجرام تيكنو
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from telegram import Update, User as TelegramUser, ChatMember, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatMemberStatus

from ..database.database import user_repo, group_repo, member_repo
from ..database.models import UserRole, ActionType
from ..ai_integration.gemini_client import gemini_client
from ..config.settings import settings

logger = logging.getLogger(__name__)

class MemberManager:
    """مدير الأعضاء"""
    
    def __init__(self):
        """تهيئة مدير الأعضاء"""
        self.welcome_messages_cache = {}
        self.verification_pending = {}
    
    async def handle_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """التعامل مع عضو جديد"""
        try:
            chat_id = update.effective_chat.id
            new_members = update.message.new_chat_members
            
            for member in new_members:
                if member.is_bot and member.id != context.bot.id:
                    # تجاهل البوتات الأخرى
                    continue
                
                # حفظ معلومات المستخدم
                user_data = {
                    'id': member.id,
                    'username': member.username,
                    'first_name': member.first_name,
                    'last_name': member.last_name,
                    'language_code': member.language_code or 'ar',
                    'is_bot': member.is_bot
                }
                
                user = user_repo.create_or_update_user(user_data)
                
                # إضافة العضو إلى المجموعة
                member_repo.add_member(member.id, chat_id)
                
                # إرسال رسالة ترحيب
                await self._send_welcome_message(update, context, member)
                
                # التحقق من العضو إذا كان مفعلاً
                group_settings = group_repo.get_group_settings(chat_id)
                if group_settings.get('features_enabled', {}).get('member_verification', False):
                    await self._start_member_verification(update, context, member)
                
                logger.info(f"تم إضافة عضو جديد: {member.first_name} ({member.id}) إلى المجموعة {chat_id}")
                
        except Exception as e:
            logger.error(f"خطأ في التعامل مع عضو جديد: {e}")
    
    async def handle_member_left(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """التعامل مع مغادرة عضو"""
        try:
            chat_id = update.effective_chat.id
            left_member = update.message.left_chat_member
            
            if left_member:
                # تحديث حالة العضوية
                member_repo.remove_member(left_member.id, chat_id)
                
                logger.info(f"غادر العضو: {left_member.first_name} ({left_member.id}) المجموعة {chat_id}")
                
        except Exception as e:
            logger.error(f"خطأ في التعامل مع مغادرة عضو: {e}")
    
    async def _send_welcome_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, member: TelegramUser):
        """إرسال رسالة ترحيب"""
        try:
            chat_id = update.effective_chat.id
            group = group_repo.get_group_by_id(chat_id)
            
            # الحصول على رسالة الترحيب المخصصة أو توليد واحدة جديدة
            welcome_message = None
            if group and group.welcome_message:
                welcome_message = group.welcome_message.format(
                    name=member.first_name,
                    username=f"@{member.username}" if member.username else member.first_name,
                    group_name=update.effective_chat.title
                )
            else:
                # توليد رسالة ترحيب باستخدام Gemini AI
                welcome_message = await gemini_client.generate_welcome_message(
                    update.effective_chat.title,
                    member.first_name
                )
            
            if not welcome_message:
                # رسالة ترحيب افتراضية
                welcome_message = f"مرحباً {member.first_name}! 🎉\n\nأهلاً وسهلاً بك في {update.effective_chat.title}.\nنتمنى لك وقتاً ممتعاً ومفيداً معنا! 😊"
            
            # إضافة أزرار تفاعلية
            keyboard = [
                [InlineKeyboardButton("📋 قواعد المجموعة", callback_data=f"rules_{chat_id}")],
                [InlineKeyboardButton("ℹ️ معلومات المجموعة", callback_data=f"info_{chat_id}")],
                [InlineKeyboardButton("🤝 تعرف على الأعضاء", callback_data=f"members_{chat_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=chat_id,
                text=welcome_message,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"خطأ في إرسال رسالة الترحيب: {e}")
    
    async def _start_member_verification(self, update: Update, context: ContextTypes.DEFAULT_TYPE, member: TelegramUser):
        """بدء عملية التحقق من العضو"""
        try:
            chat_id = update.effective_chat.id
            
            # إنشاء تحدي التحقق
            verification_code = self._generate_verification_code()
            self.verification_pending[member.id] = {
                'code': verification_code,
                'chat_id': chat_id,
                'timestamp': datetime.now(timezone.utc),
                'attempts': 0
            }
            
            # إرسال رسالة التحقق
            keyboard = [
                [InlineKeyboardButton(f"✅ {verification_code}", callback_data=f"verify_{member.id}_{verification_code}")],
                [InlineKeyboardButton("❌ رمز خاطئ", callback_data=f"verify_{member.id}_wrong1")],
                [InlineKeyboardButton("❌ رمز خاطئ", callback_data=f"verify_{member.id}_wrong2")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            verification_message = f"""
🔐 **التحقق من العضوية**

مرحباً {member.first_name}!

للتأكد من أنك لست بوت، يرجى الضغط على الزر الصحيح أدناه:

⏰ لديك 5 دقائق لإكمال التحقق
            """
            
            await context.bot.send_message(
                chat_id=chat_id,
                text=verification_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            # جدولة إزالة العضو إذا لم يتم التحقق
            context.job_queue.run_once(
                self._remove_unverified_member,
                when=300,  # 5 دقائق
                data={'user_id': member.id, 'chat_id': chat_id},
                name=f"verification_timeout_{member.id}_{chat_id}"
            )
            
        except Exception as e:
            logger.error(f"خطأ في بدء التحقق من العضو: {e}")
    
    def _generate_verification_code(self) -> str:
        """توليد رمز التحقق"""
        import random
        import string
        return ''.join(random.choices(string.digits, k=4))
    
    async def _remove_unverified_member(self, context: ContextTypes.DEFAULT_TYPE):
        """إزالة عضو لم يتم التحقق منه"""
        try:
            job_data = context.job.data
            user_id = job_data['user_id']
            chat_id = job_data['chat_id']
            
            # التحقق من أن العضو لم يتم التحقق منه بعد
            if user_id in self.verification_pending:
                # إزالة العضو من المجموعة
                await context.bot.ban_chat_member(chat_id, user_id)
                await context.bot.unban_chat_member(chat_id, user_id)
                
                # إزالة من قائمة الانتظار
                del self.verification_pending[user_id]
                
                # تسجيل الإجراء
                logger.info(f"تم إزالة العضو غير المتحقق منه: {user_id} من المجموعة {chat_id}")
                
        except Exception as e:
            logger.error(f"خطأ في إزالة العضو غير المتحقق منه: {e}")
    
    async def handle_verification_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """التعامل مع رد التحقق"""
        try:
            query = update.callback_query
            await query.answer()
            
            # تحليل البيانات
            data_parts = query.data.split('_')
            if len(data_parts) < 3:
                return
            
            user_id = int(data_parts[1])
            provided_code = data_parts[2]
            
            # التحقق من صحة الرمز
            if user_id in self.verification_pending:
                verification_data = self.verification_pending[user_id]
                correct_code = verification_data['code']
                
                if provided_code == correct_code:
                    # التحقق نجح
                    del self.verification_pending[user_id]
                    
                    # إلغاء مهمة الإزالة
                    current_jobs = context.job_queue.get_jobs_by_name(f"verification_timeout_{user_id}_{verification_data['chat_id']}")
                    for job in current_jobs:
                        job.schedule_removal()
                    
                    await query.edit_message_text(
                        text="✅ تم التحقق بنجاح! مرحباً بك في المجموعة! 🎉",
                        parse_mode='Markdown'
                    )
                    
                    logger.info(f"تم التحقق من العضو بنجاح: {user_id}")
                    
                else:
                    # الرمز خاطئ
                    verification_data['attempts'] += 1
                    
                    if verification_data['attempts'] >= 3:
                        # تجاوز عدد المحاولات المسموح
                        await context.bot.ban_chat_member(verification_data['chat_id'], user_id)
                        await context.bot.unban_chat_member(verification_data['chat_id'], user_id)
                        del self.verification_pending[user_id]
                        
                        await query.edit_message_text(
                            text="❌ تجاوزت عدد المحاولات المسموح. تم إزالتك من المجموعة.",
                            parse_mode='Markdown'
                        )
                    else:
                        await query.edit_message_text(
                            text=f"❌ رمز خاطئ. المحاولة {verification_data['attempts']}/3",
                            parse_mode='Markdown'
                        )
            
        except Exception as e:
            logger.error(f"خطأ في التعامل مع رد التحقق: {e}")
    
    async def ban_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, reason: str = None, duration: int = None):
        """حظر عضو"""
        try:
            chat_id = update.effective_chat.id
            admin_id = update.effective_user.id
            
            # التحقق من صلاحيات المشرف
            if not await self._check_admin_permissions(update, context, admin_id):
                await update.message.reply_text("❌ ليس لديك صلاحية لحظر الأعضاء.")
                return
            
            # حظر العضو
            if duration:
                # حظر مؤقت
                until_date = datetime.now(timezone.utc) + timedelta(minutes=duration)
                await context.bot.ban_chat_member(chat_id, user_id, until_date=until_date)
            else:
                # حظر دائم
                await context.bot.ban_chat_member(chat_id, user_id)
            
            # تسجيل الإجراء في قاعدة البيانات
            from ..database.database import db_manager
            from ..database.models import Action
            
            with db_manager.get_session() as session:
                action = Action(
                    group_id=chat_id,
                    performed_by_id=admin_id,
                    target_user_id=user_id,
                    action_type=ActionType.BAN,
                    reason=reason,
                    duration=duration
                )
                session.add(action)
                session.commit()
            
            # إرسال رسالة تأكيد
            user = user_repo.get_user_by_id(user_id)
            user_name = user.first_name if user else str(user_id)
            
            if duration:
                await update.message.reply_text(
                    f"✅ تم حظر {user_name} لمدة {duration} دقيقة.\n"
                    f"السبب: {reason or 'غير محدد'}"
                )
            else:
                await update.message.reply_text(
                    f"✅ تم حظر {user_name} نهائياً.\n"
                    f"السبب: {reason or 'غير محدد'}"
                )
            
            logger.info(f"تم حظر العضو {user_id} من المجموعة {chat_id} بواسطة {admin_id}")
            
        except Exception as e:
            logger.error(f"خطأ في حظر العضو: {e}")
            await update.message.reply_text("❌ حدث خطأ أثناء حظر العضو.")
    
    async def unban_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """إلغاء حظر عضو"""
        try:
            chat_id = update.effective_chat.id
            admin_id = update.effective_user.id
            
            # التحقق من صلاحيات المشرف
            if not await self._check_admin_permissions(update, context, admin_id):
                await update.message.reply_text("❌ ليس لديك صلاحية لإلغاء حظر الأعضاء.")
                return
            
            # إلغاء حظر العضو
            await context.bot.unban_chat_member(chat_id, user_id)
            
            # تسجيل الإجراء
            from ..database.database import db_manager
            from ..database.models import Action
            
            with db_manager.get_session() as session:
                action = Action(
                    group_id=chat_id,
                    performed_by_id=admin_id,
                    target_user_id=user_id,
                    action_type=ActionType.UNBAN
                )
                session.add(action)
                session.commit()
            
            # إرسال رسالة تأكيد
            user = user_repo.get_user_by_id(user_id)
            user_name = user.first_name if user else str(user_id)
            
            await update.message.reply_text(f"✅ تم إلغاء حظر {user_name}.")
            
            logger.info(f"تم إلغاء حظر العضو {user_id} من المجموعة {chat_id} بواسطة {admin_id}")
            
        except Exception as e:
            logger.error(f"خطأ في إلغاء حظر العضو: {e}")
            await update.message.reply_text("❌ حدث خطأ أثناء إلغاء حظر العضو.")
    
    async def mute_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, duration: int = None):
        """كتم صوت عضو"""
        try:
            chat_id = update.effective_chat.id
            admin_id = update.effective_user.id
            
            # التحقق من صلاحيات المشرف
            if not await self._check_admin_permissions(update, context, admin_id):
                await update.message.reply_text("❌ ليس لديك صلاحية لكتم الأعضاء.")
                return
            
            # إعداد صلاحيات الكتم
            permissions = {
                'can_send_messages': False,
                'can_send_media_messages': False,
                'can_send_polls': False,
                'can_send_other_messages': False,
                'can_add_web_page_previews': False
            }
            
            # كتم العضو
            if duration:
                until_date = datetime.now(timezone.utc) + timedelta(minutes=duration)
                await context.bot.restrict_chat_member(
                    chat_id, user_id, 
                    permissions=permissions,
                    until_date=until_date
                )
            else:
                await context.bot.restrict_chat_member(
                    chat_id, user_id,
                    permissions=permissions
                )
            
            # تسجيل الإجراء
            from ..database.database import db_manager
            from ..database.models import Action
            
            with db_manager.get_session() as session:
                action = Action(
                    group_id=chat_id,
                    performed_by_id=admin_id,
                    target_user_id=user_id,
                    action_type=ActionType.MUTE,
                    duration=duration
                )
                session.add(action)
                session.commit()
            
            # إرسال رسالة تأكيد
            user = user_repo.get_user_by_id(user_id)
            user_name = user.first_name if user else str(user_id)
            
            if duration:
                await update.message.reply_text(f"🔇 تم كتم {user_name} لمدة {duration} دقيقة.")
            else:
                await update.message.reply_text(f"🔇 تم كتم {user_name} نهائياً.")
            
            logger.info(f"تم كتم العضو {user_id} في المجموعة {chat_id} بواسطة {admin_id}")
            
        except Exception as e:
            logger.error(f"خطأ في كتم العضو: {e}")
            await update.message.reply_text("❌ حدث خطأ أثناء كتم العضو.")
    
    async def unmute_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """إلغاء كتم عضو"""
        try:
            chat_id = update.effective_chat.id
            admin_id = update.effective_user.id
            
            # التحقق من صلاحيات المشرف
            if not await self._check_admin_permissions(update, context, admin_id):
                await update.message.reply_text("❌ ليس لديك صلاحية لإلغاء كتم الأعضاء.")
                return
            
            # إعادة الصلاحيات الكاملة
            permissions = {
                'can_send_messages': True,
                'can_send_media_messages': True,
                'can_send_polls': True,
                'can_send_other_messages': True,
                'can_add_web_page_previews': True
            }
            
            await context.bot.restrict_chat_member(chat_id, user_id, permissions=permissions)
            
            # تسجيل الإجراء
            from ..database.database import db_manager
            from ..database.models import Action
            
            with db_manager.get_session() as session:
                action = Action(
                    group_id=chat_id,
                    performed_by_id=admin_id,
                    target_user_id=user_id,
                    action_type=ActionType.UNMUTE
                )
                session.add(action)
                session.commit()
            
            # إرسال رسالة تأكيد
            user = user_repo.get_user_by_id(user_id)
            user_name = user.first_name if user else str(user_id)
            
            await update.message.reply_text(f"🔊 تم إلغاء كتم {user_name}.")
            
            logger.info(f"تم إلغاء كتم العضو {user_id} في المجموعة {chat_id} بواسطة {admin_id}")
            
        except Exception as e:
            logger.error(f"خطأ في إلغاء كتم العضو: {e}")
            await update.message.reply_text("❌ حدث خطأ أثناء إلغاء كتم العضو.")
    
    async def _check_admin_permissions(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
        """التحقق من صلاحيات المشرف"""
        try:
            chat_id = update.effective_chat.id
            member = await context.bot.get_chat_member(chat_id, user_id)
            
            return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من صلاحيات المشرف: {e}")
            return False
    
    async def get_member_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """الحصول على إحصائيات الأعضاء"""
        try:
            chat_id = update.effective_chat.id
            
            # الحصول على إحصائيات من قاعدة البيانات
            members = member_repo.get_group_members(chat_id)
            
            total_members = len(members)
            active_members = len([m for m in members if m.last_activity and 
                                (datetime.now(timezone.utc) - m.last_activity).days <= 7])
            
            admins = len([m for m in members if m.role in [UserRole.ADMIN, UserRole.MODERATOR]])
            
            stats_message = f"""
📊 **إحصائيات الأعضاء**

👥 إجمالي الأعضاء: {total_members}
🟢 الأعضاء النشطون (آخر 7 أيام): {active_members}
👑 المشرفون: {admins}
📈 معدل النشاط: {(active_members/total_members*100):.1f}%

📅 آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            """
            
            await update.message.reply_text(stats_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على إحصائيات الأعضاء: {e}")
            await update.message.reply_text("❌ حدث خطأ أثناء جلب الإحصائيات.")

# إنشاء مثيل مدير الأعضاء
member_manager = MemberManager()

