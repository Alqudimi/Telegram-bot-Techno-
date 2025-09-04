"""
إدارة قاعدة البيانات لبوت تيليجرام تيكنو
"""
import logging
from typing import Optional, Any, Dict, List
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

from .models import Base, User, Group, GroupMember, Message, Action, ScheduledMessage, Poll, CustomCommand, Analytics, BotSettings
from ..config.settings import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    """مدير قاعدة البيانات"""
    
    def __init__(self, database_url: str = None):
        """تهيئة مدير قاعدة البيانات"""
        self.database_url = database_url or settings.DATABASE_URL
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self):
        """تهيئة قاعدة البيانات"""
        try:
            # إنشاء محرك قاعدة البيانات
            self.engine = create_engine(
                self.database_url,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=settings.DEBUG
            )
            
            # إنشاء جلسة قاعدة البيانات
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # إنشاء الجداول
            self.create_tables()
            
            logger.info("تم تهيئة قاعدة البيانات بنجاح")
            
        except Exception as e:
            logger.error(f"خطأ في تهيئة قاعدة البيانات: {e}")
            raise
    
    def create_tables(self):
        """إنشاء جداول قاعدة البيانات"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("تم إنشاء جداول قاعدة البيانات بنجاح")
        except Exception as e:
            logger.error(f"خطأ في إنشاء جداول قاعدة البيانات: {e}")
            raise
    
    @contextmanager
    def get_session(self):
        """الحصول على جلسة قاعدة البيانات"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"خطأ في جلسة قاعدة البيانات: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """اختبار الاتصال بقاعدة البيانات"""
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("تم اختبار الاتصال بقاعدة البيانات بنجاح")
            return True
        except Exception as e:
            logger.error(f"فشل في الاتصال بقاعدة البيانات: {e}")
            return False

class UserRepository:
    """مستودع المستخدمين"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """الحصول على مستخدم بواسطة المعرف"""
        with self.db_manager.get_session() as session:
            return session.query(User).filter(User.id == user_id).first()
    
    def create_or_update_user(self, user_data: Dict[str, Any]) -> User:
        """إنشاء أو تحديث مستخدم"""
        with self.db_manager.get_session() as session:
            user = session.query(User).filter(User.id == user_data['id']).first()
            
            if user:
                # تحديث المستخدم الموجود
                for key, value in user_data.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
            else:
                # إنشاء مستخدم جديد
                user = User(**user_data)
                session.add(user)
            
            session.commit()
            session.refresh(user)
            return user
    
    def update_user_activity(self, user_id: int):
        """تحديث نشاط المستخدم"""
        with self.db_manager.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                from datetime import datetime, timezone
                user.last_seen = datetime.now(timezone.utc)
                session.commit()
    
    def increment_user_messages(self, user_id: int):
        """زيادة عدد رسائل المستخدم"""
        with self.db_manager.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.total_messages += 1
                session.commit()

class GroupRepository:
    """مستودع المجموعات"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def get_group_by_id(self, group_id: int) -> Optional[Group]:
        """الحصول على مجموعة بواسطة المعرف"""
        with self.db_manager.get_session() as session:
            return session.query(Group).filter(Group.id == group_id).first()
    
    def create_or_update_group(self, group_data: Dict[str, Any]) -> Group:
        """إنشاء أو تحديث مجموعة"""
        with self.db_manager.get_session() as session:
            group = session.query(Group).filter(Group.id == group_data['id']).first()
            
            if group:
                # تحديث المجموعة الموجودة
                for key, value in group_data.items():
                    if hasattr(group, key):
                        setattr(group, key, value)
            else:
                # إنشاء مجموعة جديدة
                group = Group(**group_data)
                session.add(group)
            
            session.commit()
            session.refresh(group)
            return group
    
    def get_group_settings(self, group_id: int) -> Dict[str, Any]:
        """الحصول على إعدادات المجموعة"""
        group = self.get_group_by_id(group_id)
        if group:
            return {
                'filter_settings': group.filter_settings or settings.DEFAULT_FILTER_SETTINGS,
                'features_enabled': group.features_enabled or settings.FEATURES,
                'language': group.language,
                'timezone': group.timezone,
                'welcome_message': group.welcome_message,
                'rules': group.rules
            }
        return {}
    
    def update_group_settings(self, group_id: int, settings_data: Dict[str, Any]):
        """تحديث إعدادات المجموعة"""
        with self.db_manager.get_session() as session:
            group = session.query(Group).filter(Group.id == group_id).first()
            if group:
                for key, value in settings_data.items():
                    if hasattr(group, key):
                        setattr(group, key, value)
                session.commit()

class GroupMemberRepository:
    """مستودع أعضاء المجموعات"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def get_member(self, user_id: int, group_id: int) -> Optional[GroupMember]:
        """الحصول على عضو في مجموعة"""
        with self.db_manager.get_session() as session:
            return session.query(GroupMember).filter(
                GroupMember.user_id == user_id,
                GroupMember.group_id == group_id
            ).first()
    
    def add_member(self, user_id: int, group_id: int, role: str = "member") -> GroupMember:
        """إضافة عضو إلى مجموعة"""
        with self.db_manager.get_session() as session:
            # التحقق من وجود العضو
            existing_member = session.query(GroupMember).filter(
                GroupMember.user_id == user_id,
                GroupMember.group_id == group_id
            ).first()
            
            if existing_member:
                return existing_member
            
            # إنشاء عضوية جديدة
            from .models import UserRole
            member = GroupMember(
                user_id=user_id,
                group_id=group_id,
                role=UserRole(role)
            )
            session.add(member)
            session.commit()
            session.refresh(member)
            return member
    
    def remove_member(self, user_id: int, group_id: int):
        """إزالة عضو من مجموعة"""
        with self.db_manager.get_session() as session:
            member = session.query(GroupMember).filter(
                GroupMember.user_id == user_id,
                GroupMember.group_id == group_id
            ).first()
            
            if member:
                from datetime import datetime, timezone
                member.left_at = datetime.now(timezone.utc)
                session.commit()
    
    def get_group_members(self, group_id: int) -> List[GroupMember]:
        """الحصول على جميع أعضاء المجموعة"""
        with self.db_manager.get_session() as session:
            return session.query(GroupMember).filter(
                GroupMember.group_id == group_id,
                GroupMember.left_at.is_(None)
            ).all()

class MessageRepository:
    """مستودع الرسائل"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def save_message(self, message_data: Dict[str, Any]) -> Message:
        """حفظ رسالة"""
        with self.db_manager.get_session() as session:
            message = Message(**message_data)
            session.add(message)
            session.commit()
            session.refresh(message)
            return message
    
    def get_recent_messages(self, group_id: int, limit: int = 50) -> List[Message]:
        """الحصول على الرسائل الحديثة"""
        with self.db_manager.get_session() as session:
            return session.query(Message).filter(
                Message.group_id == group_id,
                Message.is_deleted == False
            ).order_by(Message.sent_at.desc()).limit(limit).all()

# إنشاء مثيل مدير قاعدة البيانات
db_manager = DatabaseManager()

# إنشاء مستودعات البيانات
user_repo = UserRepository(db_manager)
group_repo = GroupRepository(db_manager)
member_repo = GroupMemberRepository(db_manager)
message_repo = MessageRepository(db_manager)

