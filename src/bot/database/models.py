"""
نماذج قاعدة البيانات لبوت تيليجرام تيكنو
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, JSON, 
    ForeignKey, BigInteger, Float, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    """أدوار المستخدمين"""
    MEMBER = "member"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class MessageType(enum.Enum):
    """أنواع الرسائل"""
    TEXT = "text"
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"
    VOICE = "voice"
    DOCUMENT = "document"
    STICKER = "sticker"
    ANIMATION = "animation"
    LOCATION = "location"
    CONTACT = "contact"

class ActionType(enum.Enum):
    """أنواع الإجراءات"""
    BAN = "ban"
    UNBAN = "unban"
    MUTE = "mute"
    UNMUTE = "unmute"
    WARN = "warn"
    KICK = "kick"
    DELETE_MESSAGE = "delete_message"
    PROMOTE = "promote"
    DEMOTE = "demote"

class User(Base):
    """نموذج المستخدم"""
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True)  # Telegram User ID
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language_code = Column(String(10), default="ar")
    is_bot = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    
    # إعدادات المستخدم
    preferred_language = Column(String(10), default="ar")
    timezone = Column(String(50), default="UTC")
    notifications_enabled = Column(Boolean, default=True)
    
    # إحصائيات
    total_messages = Column(Integer, default=0)
    points = Column(Integer, default=0)
    warnings = Column(Integer, default=0)
    
    # تواريخ
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_seen = Column(DateTime, nullable=True)
    
    # العلاقات
    group_memberships = relationship("GroupMember", back_populates="user")
    sent_messages = relationship("Message", back_populates="user")
    actions_performed = relationship("Action", foreign_keys="Action.performed_by_id", back_populates="performed_by")
    actions_received = relationship("Action", foreign_keys="Action.target_user_id", back_populates="target_user")

class Group(Base):
    """نموذج المجموعة"""
    __tablename__ = "groups"
    
    id = Column(BigInteger, primary_key=True)  # Telegram Chat ID
    title = Column(String(255), nullable=False)
    username = Column(String(255), nullable=True)
    type = Column(String(50), nullable=False)  # group, supergroup, channel
    description = Column(Text, nullable=True)
    
    # إعدادات المجموعة
    language = Column(String(10), default="ar")
    timezone = Column(String(50), default="UTC")
    welcome_message = Column(Text, nullable=True)
    rules = Column(Text, nullable=True)
    
    # إعدادات التصفية
    filter_settings = Column(JSON, nullable=True)
    banned_words = Column(JSON, nullable=True)
    allowed_domains = Column(JSON, nullable=True)
    
    # إعدادات الميزات
    features_enabled = Column(JSON, nullable=True)
    
    # إحصائيات
    total_members = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)
    
    # حالة المجموعة
    is_active = Column(Boolean, default=True)
    maintenance_mode = Column(Boolean, default=False)
    
    # تواريخ
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # العلاقات
    members = relationship("GroupMember", back_populates="group")
    messages = relationship("Message", back_populates="group")
    actions = relationship("Action", back_populates="group")
    scheduled_messages = relationship("ScheduledMessage", back_populates="group")
    polls = relationship("Poll", back_populates="group")

class GroupMember(Base):
    """نموذج عضوية المجموعة"""
    __tablename__ = "group_members"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    group_id = Column(BigInteger, ForeignKey("groups.id"), nullable=False)
    
    # دور العضو
    role = Column(SQLEnum(UserRole), default=UserRole.MEMBER)
    
    # إعدادات العضوية
    can_send_messages = Column(Boolean, default=True)
    can_send_media = Column(Boolean, default=True)
    can_send_polls = Column(Boolean, default=True)
    can_send_other_messages = Column(Boolean, default=True)
    can_add_web_page_previews = Column(Boolean, default=True)
    can_change_info = Column(Boolean, default=False)
    can_invite_users = Column(Boolean, default=False)
    can_pin_messages = Column(Boolean, default=False)
    
    # إحصائيات العضو في المجموعة
    messages_count = Column(Integer, default=0)
    points = Column(Integer, default=0)
    warnings = Column(Integer, default=0)
    
    # حالة العضوية
    is_muted = Column(Boolean, default=False)
    mute_until = Column(DateTime, nullable=True)
    is_banned = Column(Boolean, default=False)
    ban_until = Column(DateTime, nullable=True)
    
    # تواريخ
    joined_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    left_at = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, nullable=True)
    
    # العلاقات
    user = relationship("User", back_populates="group_memberships")
    group = relationship("Group", back_populates="members")

class Message(Base):
    """نموذج الرسالة"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, nullable=False)  # Telegram Message ID
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    group_id = Column(BigInteger, ForeignKey("groups.id"), nullable=False)
    
    # محتوى الرسالة
    text = Column(Text, nullable=True)
    message_type = Column(SQLEnum(MessageType), nullable=False)
    file_id = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)
    
    # تحليل الرسالة
    sentiment_score = Column(Float, nullable=True)
    language_detected = Column(String(10), nullable=True)
    contains_spam = Column(Boolean, default=False)
    contains_profanity = Column(Boolean, default=False)
    
    # معلومات إضافية
    reply_to_message_id = Column(Integer, nullable=True)
    forward_from_user_id = Column(BigInteger, nullable=True)
    forward_from_chat_id = Column(BigInteger, nullable=True)
    
    # حالة الرسالة
    is_deleted = Column(Boolean, default=False)
    is_edited = Column(Boolean, default=False)
    
    # تواريخ
    sent_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    edited_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    
    # العلاقات
    user = relationship("User", back_populates="sent_messages")
    group = relationship("Group", back_populates="messages")

class Action(Base):
    """نموذج الإجراءات الإدارية"""
    __tablename__ = "actions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(BigInteger, ForeignKey("groups.id"), nullable=False)
    performed_by_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    target_user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    
    # تفاصيل الإجراء
    action_type = Column(SQLEnum(ActionType), nullable=False)
    reason = Column(Text, nullable=True)
    duration = Column(Integer, nullable=True)  # بالدقائق
    
    # معلومات إضافية
    message_id = Column(Integer, nullable=True)
    additional_data = Column(JSON, nullable=True)
    
    # تواريخ
    performed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True)
    
    # العلاقات
    group = relationship("Group", back_populates="actions")
    performed_by = relationship("User", foreign_keys=[performed_by_id], back_populates="actions_performed")
    target_user = relationship("User", foreign_keys=[target_user_id], back_populates="actions_received")

class ScheduledMessage(Base):
    """نموذج الرسائل المجدولة"""
    __tablename__ = "scheduled_messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(BigInteger, ForeignKey("groups.id"), nullable=False)
    created_by_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    
    # محتوى الرسالة
    text = Column(Text, nullable=False)
    message_type = Column(SQLEnum(MessageType), default=MessageType.TEXT)
    file_id = Column(String(255), nullable=True)
    
    # إعدادات الجدولة
    scheduled_for = Column(DateTime, nullable=False)
    repeat_interval = Column(Integer, nullable=True)  # بالدقائق
    repeat_count = Column(Integer, nullable=True)
    
    # حالة الرسالة
    is_sent = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # تواريخ
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    sent_at = Column(DateTime, nullable=True)
    
    # العلاقات
    group = relationship("Group", back_populates="scheduled_messages")
    created_by = relationship("User")

class Poll(Base):
    """نموذج الاستبيانات"""
    __tablename__ = "polls"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    poll_id = Column(String(255), unique=True, nullable=False)  # Telegram Poll ID
    group_id = Column(BigInteger, ForeignKey("groups.id"), nullable=False)
    created_by_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    
    # محتوى الاستبيان
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)
    
    # إعدادات الاستبيان
    is_anonymous = Column(Boolean, default=True)
    allows_multiple_answers = Column(Boolean, default=False)
    correct_option_id = Column(Integer, nullable=True)
    explanation = Column(Text, nullable=True)
    
    # حالة الاستبيان
    is_closed = Column(Boolean, default=False)
    total_voter_count = Column(Integer, default=0)
    
    # تواريخ
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    closed_at = Column(DateTime, nullable=True)
    
    # العلاقات
    group = relationship("Group", back_populates="polls")
    created_by = relationship("User")

class CustomCommand(Base):
    """نموذج الأوامر المخصصة"""
    __tablename__ = "custom_commands"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(BigInteger, ForeignKey("groups.id"), nullable=False)
    created_by_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    
    # تفاصيل الأمر
    command = Column(String(255), nullable=False)
    response = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    
    # إعدادات الأمر
    is_active = Column(Boolean, default=True)
    admin_only = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    
    # تواريخ
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_used = Column(DateTime, nullable=True)
    
    # العلاقات
    group = relationship("Group")
    created_by = relationship("User")

class Analytics(Base):
    """نموذج التحليلات والإحصائيات"""
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(BigInteger, ForeignKey("groups.id"), nullable=False)
    
    # نوع الإحصائية
    metric_type = Column(String(100), nullable=False)  # daily_messages, new_members, etc.
    metric_value = Column(Float, nullable=False)
    
    # معلومات إضافية
    meta_data = Column(JSON, nullable=True)
    
    # تاريخ الإحصائية
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # العلاقات
    group = relationship("Group")

class BotSettings(Base):
    """نموذج إعدادات البوت العامة"""
    __tablename__ = "bot_settings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(255), unique=True, nullable=False)
    value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    
    # تواريخ
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

