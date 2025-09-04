# بوت تيليجرام تيكنو (Techno) - نظام إدارة المجموعات المتقدم

## 🤖 نظرة عامة

**تيكنو** هو بوت تيليجرام متقدم ومتكامل لإدارة المجموعات بذكاء اصطناعي. يوفر أكثر من 100 وظيفة و 70 ميزة فريدة لإدارة المجموعات بكفاءة عالية.

## ✨ الميزات الرئيسية

### 👥 إدارة الأعضاء
- ترحيب تلقائي ذكي للأعضاء الجدد
- نظام التحقق من الأعضاء لمنع البوتات
- إدارة الأدوار والصلاحيات
- نظام النقاط والمكافآت
- حظر/كتم الأعضاء مع أسباب مسجلة
- تنظيف الأعضاء غير النشطين

### 🛡️ تصفية المحتوى والحماية
- مكافحة السبام المتقدمة
- فلترة الكلمات المحظورة
- تصفية الروابط والوسائط
- حماية من الفيضان (Flood Protection)
- كشف الأنماط المشبوهة
- تحليل المحتوى بالذكاء الاصطناعي

### 🤖 الذكاء الاصطناعي (Gemini AI)
- ردود ذكية على الأسئلة
- تحليل المشاعر في الرسائل
- تلخيص المحادثات الطويلة
- اقتراح المحتوى المناسب
- المساعدة في حل النزاعات
- كشف الرسائل المزعجة والمحتوى غير المناسب

### ⚙️ واجهة الإدارة المتقدمة
- لوحة تحكم تفاعلية داخل تيليجرام
- إدارة جميع الإعدادات من مكان واحد
- تخصيص الرسائل والردود
- إدارة الميزات والوظائف
- عرض الإحصائيات والتقارير

### 📊 الإحصائيات والتحليلات
- إحصائيات مفصلة عن الأعضاء
- تقارير النشاط والتفاعل
- تحليل أداء المجموعة
- تصدير البيانات والتقارير

### 🌍 ميزات إضافية
- دعم متعدد اللغات (8 لغات)
- رسائل مجدولة
- استبيانات واختبارات
- أوامر مخصصة
- تكامل مع خدمات خارجية
- نسخ احتياطي واستعادة البيانات

## 🚀 التثبيت والإعداد

### المتطلبات الأساسية

- Python 3.11 أو أحدث
- PostgreSQL (أو SQLite للاختبار)
- Redis (اختياري)
- مفتاح Telegram Bot Token
- مفتاح Google Gemini AI API

### خطوات التثبيت

1. **استنساخ المشروع:**
```bash
git clone https://github.com/Alqudimi/Telegram-bot-Techno-.git
cd techno_bot
```

2. **إنشاء بيئة افتراضية:**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# أو
venv\\Scripts\\activate  # Windows
```

3. **تثبيت التبعيات:**
```bash
pip install -r requirements.txt
```

4. **إعداد متغيرات البيئة:**
```bash
cp .env.example .env
# قم بتعديل ملف .env وإضافة المفاتيح المطلوبة
```

5. **إعداد قاعدة البيانات:**
```bash
# للاختبار مع SQLite (افتراضي)
# لا حاجة لإعداد إضافي

# للإنتاج مع PostgreSQL
createdb techno_bot_db
```

6. **اختبار البوت:**
```bash
python3 test_bot.py
```

7. **تشغيل البوت:**
```bash
python3 src/main.py
```

## ⚙️ الإعدادات

### ملف .env

```env
# إعدادات تيليجرام
TELEGRAM_BOT_TOKEN=your_bot_token_here
BOT_NAME=Techno
BOT_USERNAME=your_bot_username

# إعدادات Gemini AI
GEMINI_API_KEY=your_gemini_api_key_here

# إعدادات قاعدة البيانات
DATABASE_URL=postgresql://user:password@localhost:5432/techno_bot_db
# أو للاختبار:
# DATABASE_URL=sqlite:///./techno_bot.db

# إعدادات Redis (اختياري)
REDIS_URL=redis://localhost:6379/0

# إعدادات التطبيق
DEBUG=False
LOG_LEVEL=INFO
```

### الحصول على المفاتيح المطلوبة

#### Telegram Bot Token:
1. تحدث مع [@BotFather](https://t.me/BotFather) في تيليجرام
2. أرسل `/newbot` واتبع التعليمات
3. احفظ الـ Token المُعطى

#### Google Gemini AI API Key:
1. اذهب إلى [Google AI Studio](https://makersuite.google.com/app/apikey)
2. أنشئ مفتاح API جديد
3. احفظ المفتاح

## 📖 دليل الاستخدام

### الأوامر الأساسية

#### للمستخدمين العاديين:
- `/start` - بدء البوت
- `/help` - عرض المساعدة
- `/info` - معلومات البوت
- `/stats` - إحصائيات المجموعة
- `/rules` - قواعد المجموعة
- `/ask [سؤال]` - طرح سؤال للذكاء الاصطناعي

#### للمشرفين:
- `/setup` - إعداد البوت في المجموعة
- `/settings` - فتح لوحة الإدارة
- `/ban [معرف/رد] [مدة] [سبب]` - حظر عضو
- `/unban [معرف]` - إلغاء حظر عضو
- `/mute [معرف/رد] [مدة]` - كتم عضو
- `/unmute [معرف/رد]` - إلغاء كتم عضو
- `/warn [معرف/رد] [سبب]` - تحذير عضو
- `/addword [كلمة]` - إضافة كلمة محظورة
- `/delword [كلمة]` - حذف كلمة محظورة
- `/summarize` - تلخيص المحادثة

### واجهة الإدارة

استخدم الأمر `/settings` لفتح لوحة الإدارة التفاعلية التي تتيح لك:

- **إدارة الأعضاء:** عرض قوائم الأعضاء، المحظورين، المكتومين
- **إعدادات الحماية:** تفعيل/إلغاء تفعيل مرشحات المحتوى
- **الذكاء الاصطناعي:** إدارة الردود التلقائية والميزات الذكية
- **المحتوى:** تخصيص رسائل الترحيب والقواعد
- **الإحصائيات:** عرض تقارير مفصلة عن نشاط المجموعة

## 🏗️ البنية المعمارية

```
techno_bot/
├── src/
│   ├── bot/
│   │   ├── handlers/          # معالجات الأوامر والرسائل
│   │   ├── modules/           # الوحدات الوظيفية
│   │   ├── admin_interface/   # واجهة الإدارة
│   │   ├── ai_integration/    # تكامل الذكاء الاصطناعي
│   │   ├── database/          # طبقة قاعدة البيانات
│   │   └── config/            # إدارة الإعدادات
│   ├── utils/                 # أدوات مساعدة
│   └── main.py               # نقطة الدخول الرئيسية
├── tests/                     # الاختبارات
├── docs/                      # الوثائق
├── data/                      # بيانات المشروع
├── requirements.txt           # التبعيات
├── .env.example              # مثال متغيرات البيئة
└── README.md                 # هذا الملف
```

## 🧪 الاختبارات

```bash
# تشغيل اختبارات النظام
python3 test_bot.py

# تشغيل اختبارات الوحدة (إذا توفرت)
pytest tests/
```

## 📊 قاعدة البيانات

يستخدم البوت SQLAlchemy ORM مع دعم لقواعد البيانات التالية:
- PostgreSQL (للإنتاج)
- SQLite (للاختبار والتطوير)

### الجداول الرئيسية:
- `users` - معلومات المستخدمين
- `groups` - معلومات المجموعات
- `group_members` - عضوية المجموعات
- `messages` - الرسائل المحفوظة
- `actions` - سجل الإجراءات الإدارية
- `scheduled_messages` - الرسائل المجدولة
- `polls` - الاستبيانات
- `custom_commands` - الأوامر المخصصة
- `analytics` - بيانات التحليلات

## 🔧 التخصيص والتطوير

### إضافة ميزات جديدة

1. **إنشاء وحدة جديدة:**
```python
# src/bot/modules/my_feature.py
class MyFeature:
    async def handle_something(self, update, context):
        # منطق الميزة
        pass
```

2. **تسجيل المعالجات:**
```python
# في src/main.py
from bot.modules.my_feature import MyFeature
# إضافة المعالجات المطلوبة
```

3. **إضافة إعدادات:**
```python
# في src/bot/config/settings.py
# إضافة الإعدادات الجديدة
```

### إضافة أوامر مخصصة

```python
async def my_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبا من الأمر المخصص!")

# تسجيل الأمر
application.add_handler(CommandHandler("mycommand", my_command))
```

## 🚀 النشر

### النشر على خادم Linux

1. **إعداد الخادم:**
```bash
sudo apt update
sudo apt install python3 python3-pip postgresql redis-server
```

2. **إعداد قاعدة البيانات:**
```bash
sudo -u postgres createuser techno_bot
sudo -u postgres createdb techno_bot_db -O techno_bot
```

3. **إعداد البوت:**
```bash
git clone <repository>
cd techno_bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **إعداد خدمة systemd:**
```ini
# /etc/systemd/system/techno-bot.service
[Unit]
Description=Techno Telegram Bot
After=network.target

[Service]
Type=simple
User=techno
WorkingDirectory=/path/to/techno_bot
Environment=PATH=/path/to/techno_bot/venv/bin
ExecStart=/path/to/techno_bot/venv/bin/python src/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

5. **تشغيل الخدمة:**
```bash
sudo systemctl enable techno-bot
sudo systemctl start techno-bot
```

### النشر باستخدام Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY .env .

CMD ["python", "src/main.py"]
```

## 🔒 الأمان

- جميع المفاتيح السرية محفوظة في متغيرات البيئة
- تشفير البيانات الحساسة
- تسجيل جميع الإجراءات الإدارية
- حماية من هجمات الفيضان والسبام
- التحقق من صلاحيات المستخدمين

## 📝 السجلات

يتم حفظ السجلات في:
- `techno_bot.log` - سجل التطبيق
- قاعدة البيانات - سجل الإجراءات الإدارية

## 🐛 استكشاف الأخطاء

### مشاكل شائعة:

1. **خطأ في الاتصال بقاعدة البيانات:**
   - تأكد من صحة `DATABASE_URL`
   - تأكد من تشغيل PostgreSQL

2. **خطأ في Gemini AI:**
   - تأكد من صحة `GEMINI_API_KEY`
   - تحقق من حصة API

3. **البوت لا يستجيب:**
   - تأكد من صحة `TELEGRAM_BOT_TOKEN`
   - تحقق من صلاحيات البوت في المجموعة

## 📞 الدعم

- **الإبلاغ عن الأخطاء:** [GitHub Issues](https://github.com/your-repo/issues)
- **الوثائق:** [Wiki](https://github.com/your-repo/wiki)
- **المجتمع:** [Telegram Group](https://t.me/techno_support)

## 📄 الترخيص

هذا المشروع مرخص تحت رخصة MIT. راجع ملف `LICENSE` للتفاصيل.

## 🙏 شكر وتقدير

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Google Generative AI](https://ai.google.dev/)
- [SQLAlchemy](https://www.sqlalchemy.org/)

---

**تم تطوير هذا البوت بعناية فائقة ليكون الحل الأمثل لإدارة مجموعات تيليجرام. نتمنى أن يخدم احتياجاتكم بأفضل شكل ممكن! 🚀**

