# دليل التثبيت والإعداد - بوت تيليجرام تيكنو

## 📋 المتطلبات الأساسية

### متطلبات النظام
- **نظام التشغيل:** Linux (Ubuntu 20.04+), macOS, Windows 10+
- **Python:** الإصدار 3.11 أو أحدث
- **الذاكرة:** 512 MB RAM كحد أدنى (2 GB موصى به)
- **التخزين:** 1 GB مساحة فارغة
- **الشبكة:** اتصال إنترنت مستقر

### الخدمات المطلوبة
- **قاعدة البيانات:** PostgreSQL 12+ (أو SQLite للاختبار)
- **Redis:** الإصدار 6+ (اختياري للتخزين المؤقت)
- **مفاتيح API:**
  - Telegram Bot Token
  - Google Gemini AI API Key

## 🔑 الحصول على المفاتيح المطلوبة

### 1. إنشاء بوت تيليجرام

1. **فتح محادثة مع BotFather:**
   - ابحث عن `@BotFather` في تيليجرام
   - ابدأ محادثة معه

2. **إنشاء بوت جديد:**
   ```
   /newbot
   ```

3. **اختيار اسم البوت:**
   ```
   اسم البوت: تيكنو - مدير المجموعات
   ```

4. **اختيار معرف البوت:**
   ```
   معرف البوت: techno_manager_bot
   ```

5. **حفظ Token:**
   - احفظ الـ Token المُعطى (مثل: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

6. **إعداد صلاحيات البوت:**
   ```
   /setprivacy - Disable (لقراءة جميع الرسائل)
   /setjoingroups - Enable (للانضمام للمجموعات)
   /setcommands - إعداد قائمة الأوامر
   ```

### 2. الحصول على مفتاح Gemini AI

1. **زيارة Google AI Studio:**
   - اذهب إلى: https://makersuite.google.com/app/apikey

2. **تسجيل الدخول:**
   - استخدم حساب Google الخاص بك

3. **إنشاء مفتاح API:**
   - انقر على "Create API Key"
   - اختر مشروع Google Cloud أو أنشئ جديد
   - احفظ المفتاح المُعطى

4. **تفعيل Generative AI API:**
   - اذهب إلى Google Cloud Console
   - فعّل "Generative Language API"

## 🛠︄1�7 التثبيت خطوة بخطوة

### الطريقة الأولى: التثبيت العادي

#### 1. تحضير البيئة

**على Ubuntu/Debian:**
```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت Python والأدوات المطلوبة
sudo apt install python3.11 python3.11-venv python3-pip git postgresql postgresql-contrib redis-server -y

# تثبيت مكتبات النظام المطلوبة
sudo apt install build-essential libpq-dev python3.11-dev -y
```

**على CentOS/RHEL:**
```bash
# تحديث النظام
sudo yum update -y

# تثبيت Python والأدوات
sudo yum install python3.11 python3-pip git postgresql postgresql-server redis -y

# تثبيت مكتبات التطوير
sudo yum groupinstall "Development Tools" -y
sudo yum install postgresql-devel python3-devel -y
```

**على macOS:**
```bash
# تثبيت Homebrew إذا لم يكن مثبتاً
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# تثبيت المتطلبات
brew install python@3.11 postgresql redis git
```

**على Windows:**
```powershell
# تثبيت Python من الموقع الرسمي
# تحميل وتثبيت PostgreSQL
# تحميل وتثبيت Redis
# تثبيت Git
```

#### 2. إعداد قاعدة البيانات

**PostgreSQL:**
```bash
# بدء خدمة PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# إنشاء مستخدم وقاعدة بيانات
sudo -u postgres psql
```

```sql
-- في PostgreSQL shell
CREATE USER techno_bot WITH PASSWORD 'strong_password_here';
CREATE DATABASE techno_bot_db OWNER techno_bot;
GRANT ALL PRIVILEGES ON DATABASE techno_bot_db TO techno_bot;
\q
```

**Redis (اختياري):**
```bash
# بدء خدمة Redis
sudo systemctl start redis
sudo systemctl enable redis

# اختبار Redis
redis-cli ping
# يجب أن يرد: PONG
```

#### 3. تحميل وإعداد المشروع

```bash
# إنشاء مجلد للمشروع
mkdir -p ~/bots/techno_bot
cd ~/bots/techno_bot

# تحميل المشروع (استبدل بالرابط الصحيح)
git clone https://github.com/Alqudimi/Telegram-bot-Techno-.git .
# أو إذا كان لديك ملف مضغوط:
# unzip techno_bot.zip

# إنشاء بيئة افتراضية
python3.11 -m venv venv

# تفعيل البيئة الافتراضية
source venv/bin/activate  # Linux/Mac
# أو على Windows:
# venv\Scripts\activate

# ترقية pip
pip install --upgrade pip

# تثبيت التبعيات
pip install -r requirements.txt
```

#### 4. إعداد متغيرات البيئة

```bash
# نسخ ملف الإعدادات المثال
cp .env.example .env

# تعديل الإعدادات
nano .env  # أو استخدم محرر نصوص آخر
```

**محتوى ملف .env:**
```env
# إعدادات تيليجرام
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
BOT_NAME=تيكنو
BOT_USERNAME=techno_manager_bot

# إعدادات Gemini AI
GEMINI_API_KEY=your_gemini_api_key_here

# إعدادات قاعدة البيانات
DATABASE_URL=postgresql://techno_bot:strong_password_here@localhost:5432/techno_bot_db

# إعدادات Redis (اختياري)
REDIS_URL=redis://localhost:6379/0

# إعدادات التطبيق
DEBUG=False
LOG_LEVEL=INFO
SECRET_KEY=generate_random_secret_key_here
ENCRYPTION_KEY=generate_random_encryption_key_here

# إعدادات الأداء
MAX_WORKERS=10
RATE_LIMIT_MESSAGES_PER_MINUTE=30
CACHE_TTL_SECONDS=3600
```

#### 5. اختبار التثبيت

```bash
# اختبار البوت
python3 test_bot.py

# إذا نجحت جميع الاختبارات، شغّل البوت
python3 src/main.py
```

### الطريقة الثانية: التثبيت باستخدام Docker

#### 1. إعداد Docker

```bash
# تثبيت Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# تثبيت Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. إعداد ملفات Docker

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

# تثبيت متطلبات النظام
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# إعداد مجلد العمل
WORKDIR /app

# نسخ وتثبيت التبعيات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ الكود
COPY src/ ./src/
COPY .env .

# تشغيل البوت
CMD ["python", "src/main.py"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  techno-bot:
    build: .
    restart: unless-stopped
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql://techno_bot:password@postgres:5432/techno_bot_db
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data

  postgres:
    image: postgres:15
    restart: unless-stopped
    environment:
      POSTGRES_DB: techno_bot_db
      POSTGRES_USER: techno_bot
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

volumes:
  postgres_data:
  redis_data:
```

#### 3. تشغيل البوت مع Docker

```bash
# بناء وتشغيل الحاويات
docker-compose up -d

# مراقبة السجلات
docker-compose logs -f techno-bot

# إيقاف البوت
docker-compose down
```

## 🔧 إعداد البوت في تيليجرام

### 1. إضافة البوت إلى المجموعة

1. **إضافة البوت:**
   - اذهب إلى مجموعتك
   - انقر على اسم المجموعة ↄ1�7 "Add Members"
   - ابحث عن معرف البوت وأضفه

2. **منح صلاحيات المشرف:**
   - اذهب إلى إعدادات المجموعة
   - "Administrators" ↄ1�7 "Add Admin"
   - اختر البوت ومنحه الصلاحيات التالية:
     - Delete Messages
     - Ban Users
     - Invite Users
     - Pin Messages
     - Manage Video Chats

### 2. إعداد البوت الأولي

```
# في المجموعة، أرسل:
/start

# ثم أرسل:
/setup
```

اتبع التعليمات التفاعلية لإعداد:
- إعدادات الحماية
- رسائل الترحيب
- قواعد المجموعة
- ميزات الذكاء الاصطناعي

## 🚀 تشغيل البوت كخدمة

### على Linux (systemd)

#### 1. إنشاء ملف الخدمة

```bash
sudo nano /etc/systemd/system/techno-bot.service
```

```ini
[Unit]
Description=Techno Telegram Bot
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=techno
Group=techno
WorkingDirectory=/home/techno/bots/techno_bot
Environment=PATH=/home/techno/bots/techno_bot/venv/bin
ExecStart=/home/techno/bots/techno_bot/venv/bin/python src/main.py
Restart=always
RestartSec=10

# أمان إضافي
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/techno/bots/techno_bot

[Install]
WantedBy=multi-user.target
```

#### 2. تفعيل وتشغيل الخدمة

```bash
# إعادة تحميل systemd
sudo systemctl daemon-reload

# تفعيل الخدمة للبدء التلقائي
sudo systemctl enable techno-bot

# تشغيل الخدمة
sudo systemctl start techno-bot

# فحص حالة الخدمة
sudo systemctl status techno-bot

# مراقبة السجلات
sudo journalctl -u techno-bot -f
```

## 📊 مراقبة الأداء

### السجلات

```bash
# عرض السجلات الحية
tail -f techno_bot.log

# البحث في السجلات
grep "ERROR" techno_bot.log

# تنظيف السجلات القديمة
find . -name "*.log" -mtime +30 -delete
```

### مراقبة قاعدة البيانات

```sql
-- فحص حجم قاعدة البيانات
SELECT pg_size_pretty(pg_database_size('techno_bot_db'));

-- فحص عدد الجداول والسجلات
SELECT schemaname,tablename,n_tup_ins,n_tup_upd,n_tup_del 
FROM pg_stat_user_tables;
```

### مراقبة الذاكرة والمعالج

```bash
# استخدام الذاكرة
ps aux | grep python | grep techno

# مراقبة مستمرة
htop
```

## 🔒 الأمان والنسخ الاحتياطي

### تأمين الخادم

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# إعداد جدار الحماية
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# تأمين PostgreSQL
sudo nano /etc/postgresql/15/main/postgresql.conf
# غيّر: listen_addresses = 'localhost'

sudo nano /etc/postgresql/15/main/pg_hba.conf
# تأكد من استخدام md5 للمصادقة
```

### النسخ الاحتياطي

```bash
# إنشاء سكريبت النسخ الاحتياطي
nano backup.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/techno/backups"

# إنشاء مجلد النسخ الاحتياطي
mkdir -p $BACKUP_DIR

# نسخ احتياطي لقاعدة البيانات
pg_dump -h localhost -U techno_bot techno_bot_db > $BACKUP_DIR/db_backup_$DATE.sql

# نسخ احتياطي للملفات
tar -czf $BACKUP_DIR/files_backup_$DATE.tar.gz /home/techno/bots/techno_bot

# حذف النسخ القديمة (أكثر من 30 يوم)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "تم إنشاء النسخة الاحتياطية: $DATE"
```

```bash
# جعل السكريبت قابل للتنفيذ
chmod +x backup.sh

# إضافة مهمة cron للنسخ الاحتياطي اليومي
crontab -e
# أضف: 0 2 * * * /home/techno/backup.sh
```

## 🐛 استكشاف الأخطاء الشائعة

### 1. خطأ في الاتصال بقاعدة البيانات

**الخطأ:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**الحل:**
```bash
# فحص حالة PostgreSQL
sudo systemctl status postgresql

# إعادة تشغيل PostgreSQL
sudo systemctl restart postgresql

# فحص الاتصال
psql -h localhost -U techno_bot -d techno_bot_db
```

### 2. خطأ في مفتاح Telegram

**الخطأ:**
```
telegram.error.InvalidToken: Invalid token
```

**الحل:**
- تأكد من صحة `TELEGRAM_BOT_TOKEN` في ملف `.env`
- تأكد من عدم وجود مسافات إضافية
- أنشئ بوت جديد إذا لزم الأمر

### 3. خطأ في Gemini AI

**الخطأ:**
```
google.api_core.exceptions.Unauthenticated: 401 API key not valid
```

**الحل:**
- تأكد من صحة `GEMINI_API_KEY`
- تأكد من تفعيل Generative Language API
- فحص حصة API المتبقية

### 4. البوت لا يستجيب في المجموعة

**الأسباب المحتملة:**
- البوت ليس مشرف في المجموعة
- إعدادات الخصوصية تمنع قراءة الرسائل
- البوت محظور أو مكتوم

**الحل:**
```
# في المجموعة:
/start
/help

# فحص صلاحيات البوت
# إعدادات المجموعة ↄ1�7 Administrators
```

### 5. استهلاك عالي للذاكرة

**الحل:**
```bash
# فحص استخدام الذاكرة
free -h

# إعادة تشغيل البوت
sudo systemctl restart techno-bot

# تقليل MAX_WORKERS في .env
MAX_WORKERS=5
```

## 📞 الحصول على المساعدة

### الموارد المفيدة

- **الوثائق الرسمية:** [README.md](README.md)
- **أمثلة الاستخدام:** مجلد `examples/`
- **الأسئلة الشائعة:** [FAQ.md](FAQ.md)

### التواصل للدعم

- **GitHub Issues:** للإبلاغ عن الأخطاء
- **Telegram:** @techno_support
- **البريد الإلكتروني:** support@techno-bot.com

---

**تهانينا! 🎉 تم تثبيت بوت تيكنو بنجاح. استمتع بإدارة مجموعاتك بذكاء وكفاءة!**

