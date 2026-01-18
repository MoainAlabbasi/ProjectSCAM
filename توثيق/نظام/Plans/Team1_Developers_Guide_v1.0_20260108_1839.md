# دليل العمل التفصيلي للفريق الأول (المبرمجين)

## مقدمة

هذا الدليل يقدم خطوات تفصيلية (Step-by-Step) للفريق الأول (أنت ومهند) لتطوير مشروع S-ACM. سيتم التركيز على استخدام Docker لتوحيد بيئة العمل، PostgreSQL كقاعدة بيانات، Django كإطار عمل، ودمج Gemini API للذكاء الاصطناعي، بالإضافة إلى سير عمل Git/GitHub.

---

## 🛠️ الأدوات والتقنيات المستخدمة

| الأداة/التقنية | الوصف |
|---|---|
| **نظام التشغيل** | Linux (Ubuntu), macOS, Windows (مع WSL2) |
| **بيئة التطوير المتكاملة (IDE)** | VS Code (موصى به) أو PyCharm |
| **إدارة الحاويات** | Docker و Docker Compose |
| **لغة البرمجة** | Python 3.11+ |
| **إطار العمل** | Django 5.x |
| **قاعدة البيانات** | PostgreSQL |
| **نظام التحكم بالإصدارات** | Git و GitHub |
| **واجهة برمجة تطبيقات الذكاء الاصطناعي** | Google Gemini API |
| **تخزين الملفات السحابي** | Telegram أو OneDrive (سيتم تحديد الأفضل لاحقاً) |

---

## 🚀 الخطوات التفصيلية (Step-by-Step)

### المرحلة 1: الإعداد الأولي لبيئة التطوير (اليوم 1-2)

#### 1.1. تثبيت المتطلبات الأساسية

- **تثبيت Git:**
  ```bash
  sudo apt update
  sudo apt install git
  ```
- **تثبيت Docker و Docker Compose:**
  - اتبع التعليمات الرسمية لتثبيت Docker Engine و Docker Compose على نظام التشغيل الخاص بك.
  - **لـ Ubuntu:** [Install Docker Engine](https://docs.docker.com/engine/install/ubuntu/) و [Install Docker Compose](https://docs.docker.com/compose/install/)
  - **لـ Windows (مع WSL2):** [Install Docker Desktop](https://docs.docker.com/desktop/install/windows-install/)
- **تثبيت VS Code (موصى به):**
  - قم بتنزيل وتثبيت VS Code من [الموقع الرسمي](https://code.visualstudio.com/).
  - **الإضافات الأساسية:** Python, Django, Docker, GitLens, Prettier.

#### 1.2. استنساخ المستودع من GitHub

- **أنت (معين):** قم بإنشاء مستودع المشروع الرئيسي (مثلاً `S-ACM-Project`) على GitHub. ثم قم باستنساخه:
  ```bash
  git clone https://github.com/YourUsername/S-ACM-Project.git
  cd S-ACM-Project
  ```
- **مهند:** قم باستنساخ المستودع الذي أنشأته:
  ```bash
  git clone https://github.com/MoainAlabbasi/S-ACM-Project.git # استبدل MoainAlabbasi باسم المستخدم الخاص بك
  cd S-ACM-Project
  ```

#### 1.3. إعداد Docker Compose للمشروع

- **إنشاء ملف `docker-compose.yml`:** في الجذر الرئيسي للمشروع، أنشئ الملف التالي:
  ```yaml
  # docker-compose.yml
  version: '3.8'

  services:
    db:
      image: postgres:13
      environment:
        POSTGRES_DB: ${DB_NAME}
        POSTGRES_USER: ${DB_USER}
        POSTGRES_PASSWORD: ${DB_PASSWORD}
      volumes:
        - postgres_data:/var/lib/postgresql/data/
      ports:
        - 
5432:5432

    web:
      build: .
      command: python manage.py runserver 0.0.0.0:8000
      volumes:
        - .:/app
      ports:
        - "8000:8000"
      environment:
        DB_NAME: ${DB_NAME}
        DB_USER: ${DB_USER}
        DB_PASSWORD: ${DB_PASSWORD}
        DB_HOST: db
        DB_PORT: 5432
        SECRET_KEY: ${SECRET_KEY}
        DEBUG: ${DEBUG}
        GEMINI_API_KEY: ${GEMINI_API_KEY}
      depends_on:
        - db

  volumes:
    postgres_data:
  ```

- **إنشاء ملف `Dockerfile`:** في الجذر الرئيسي للمشروع، أنشئ الملف التالي:
  ```dockerfile
  # Dockerfile
  FROM python:3.11-slim-buster

  WORKDIR /app

  ENV PYTHONUNBUFFERED 1

  COPY requirements.txt /app/
  RUN pip install --no-cache-dir -r requirements.txt

  COPY . /app/
  ```

- **إنشاء ملف `requirements.txt`:** في الجذر الرئيسي للمشروع، أنشئ الملف التالي:
  ```
  Django==5.0.1
  psycopg2-binary
  python-dotenv
  google-generativeai
  # أضف أي مكتبات أخرى تحتاجها
  ```

- **إنشاء ملف `.env`:** في الجذر الرئيسي للمشروع، أنشئ الملف التالي (لا ترفع هذا الملف إلى GitHub!):
  ```
  DB_NAME=acm_db
  DB_USER=acm_user
  DB_PASSWORD=your_db_password
  SECRET_KEY=your_django_secret_key_here
  DEBUG=True
  GEMINI_API_KEY=your_gemini_api_key_here
  ```

- **بناء وتشغيل الحاويات:**
  ```bash
  docker-compose build
  docker-compose up -d
  ```
  - تأكد من أن كل شيء يعمل بشكل صحيح بزيارة `http://localhost:8000`.

#### 1.4. إعداد مشروع Django

- **إنشاء مشروع Django:**
  ```bash
  docker-compose exec web django-admin startproject acm_project .
  ```
- **إنشاء تطبيق Django:**
  ```bash
  docker-compose exec web python manage.py startapp core
  ```
- **تعديل `acm_project/settings.py`:**
  - أضف `core` إلى `INSTALLED_APPS`.
  - قم بتكوين قاعدة البيانات لاستخدام PostgreSQL مع متغيرات البيئة:
    ```python
    import os
    from dotenv import load_dotenv

    load_dotenv()

    # ...

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
            'PORT': os.getenv('DB_PORT'),
        }
    }

    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = os.getenv('DEBUG') == 'True'
    ```

- **تطبيق الترحيلات (Migrations):**
  ```bash
  docker-compose exec web python manage.py makemigrations
  docker-compose exec web python manage.py migrate
  ```

- **إنشاء مستخدم مدير (Superuser):**
  ```bash
  docker-compose exec web python manage.py createsuperuser
  ```

### المرحلة 2: بناء نماذج البيانات (Models) (اليوم 3-4)

- **ترجمة ERD إلى `core/models.py`:**
  - قم بإنشاء جميع النماذج (Classes) بناءً على مخطط ERD في وثيقة المشروع.
  - استخدم `ForeignKey`, `ManyToManyField` لتعريف العلاقات.
  - أمثلة:
    ```python
    # core/models.py
    from django.db import models
    from django.contrib.auth.models import AbstractUser

    class User(AbstractUser):
        USER_ROLES = (
            ('student', 'Student'),
            ('doctor', 'Doctor'),
            ('admin', 'Admin'),
        )
        role = models.CharField(max_length=10, choices=USER_ROLES, default='student')

    class Major(models.Model):
        name = models.CharField(max_length=100, unique=True)

    class Level(models.Model):
        name = models.CharField(max_length=100, unique=True)

    class Course(models.Model):
        name = models.CharField(max_length=200)
        code = models.CharField(max_length=20, unique=True)
        major = models.ForeignKey(Major, on_delete=models.CASCADE)
        level = models.ForeignKey(Level, on_delete=models.CASCADE)
        doctors = models.ManyToManyField(User, related_name='taught_courses')

    class LectureFile(models.Model):
        title = models.CharField(max_length=255)
        file = models.FileField(upload_to='lectures/')
        course = models.ForeignKey(Course, on_delete=models.CASCADE)
        uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
        uploaded_at = models.DateTimeField(auto_now_add=True)
    ```
- **تطبيق الترحيلات:**
  ```bash
  docker-compose exec web python manage.py makemigrations
  docker-compose exec web python manage.py migrate
  ```
- **تسجيل النماذج في `core/admin.py`:**
  ```python
  # core/admin.py
  from django.contrib import admin
  from .models import User, Major, Level, Course, LectureFile

  admin.site.register(User)
  admin.site.register(Major)
  admin.site.register(Level)
  admin.site.register(Course)
  admin.site.register(LectureFile)
  ```

### المرحلة 3: بناء نظام المستخدمين والصلاحيات (اليوم 5-6)

- **تعديل `acm_project/urls.py`:**
  ```python
  # acm_project/urls.py
  from django.contrib import admin
  from django.urls import path, include

  urlpatterns = [
      path('admin/', admin.site.urls),
      path('', include('core.urls')),
  ]
  ```
- **إنشاء `core/urls.py`:**
  ```python
  # core/urls.py
  from django.urls import path
  from . import views

  urlpatterns = [
      path('', views.home, name='home'),
      path('login/', views.user_login, name='login'),
      path('logout/', views.user_logout, name='logout'),
      path('register/', views.user_register, name='register'),
      # أضف مسارات أخرى هنا
  ]
  ```
- **كتابة الـ Views للمصادقة في `core/views.py`:**
  - استخدم `django.contrib.auth.views` للوظائف الأساسية.
  - قم بإنشاء نماذج (Forms) لتسجيل الدخول والتسجيل.
- **إنشاء قوالب HTML للمصادقة:**
  - `templates/registration/login.html`
  - `templates/registration/register.html`
  - `templates/home.html`

### المرحلة 4: تطوير وظائف إدارة المحتوى (اليوم 7-9)

- **واجهة رفع الملفات للمدرس:**
  - في `core/views.py`، أنشئ `view` لرفع الملفات.
  - في `core/urls.py`، أضف مساراً لهذا الـ `view`.
  - في `templates/core/doctor_upload.html`، أنشئ نموذج رفع الملفات.
- **واجهة عرض الملفات للطالب:**
  - في `core/views.py`، أنشئ `view` لعرض المقررات والملفات.
  - في `core/urls.py`، أضف مساراً لهذا الـ `view`.
  - في `templates/core/student_courses.html`، أنشئ قالب لعرض المحتوى.
- **تطبيق الصلاحيات:**
  - استخدم `decorators` مثل `@login_required` و `@user_passes_test` لحماية الـ `views` بناءً على دور المستخدم.

### المرحلة 5: نظام الإشعارات ولوحات التحكم (اليوم 10-11)

- **نظام الإشعارات:**
  - أنشئ نموذج `Notification` في `core/models.py`.
  - أنشئ `view` للمدرس لإرسال الإشعارات.
  - أنشئ `view` للطالب لعرض الإشعارات.
- **لوحات التحكم:**
  - صمم قوالب HTML لـ `admin_dashboard.html` و `doctor_dashboard.html`.
  - أنشئ `views` لجلب البيانات اللازمة وعرضها في لوحات التحكم.

### المرحلة 6: دمج الذكاء الاصطناعي (Gemini API) (اليوم 12-13)

- **تثبيت مكتبة Gemini:** (تمت إضافتها في `requirements.txt`)
- **تكوين Gemini API:**
  ```python
  # في ملف مثل acm_project/ai_config.py أو مباشرة في views.py
  import google.generativeai as genai
  import os

  genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
  model = genai.GenerativeModel('gemini-pro')
  ```
- **وظيفة تلخيص المحاضرات:**
  - أنشئ `view` يستقبل نص المحاضرة.
  - استخدم `model.generate_content(f"لخص النص التالي: {lecture_text}")`.
  - اعرض الملخص للطالب.
- **وظيفة توليد الأسئلة:**
  - أنشئ `view` يستقبل نص المحاضرة.
  - استخدم `model.generate_content(f"من النص التالي، قم بتوليد 5 أسئلة مع خيارات متعددة وإجاباتها: {lecture_text}")`.
  - اعرض الأسئلة للطالب.

### المرحلة 7: الاختبار والنشر (اليوم 14-15)

- **الاختبار:**
  - قم بإجراء اختبارات يدوية مكثفة لجميع الوظائف.
  - استخدم لوحة تحكم Django لإدخال بيانات اختبار متنوعة.
  - تعاون مع الفريق الثاني للإبلاغ عن الأخطاء عبر GitHub Issues.
- **التهيئة للنشر:**
  - تأكد من أن `DEBUG = False` في `settings.py`.
  - قم بتعيين `ALLOWED_HOSTS`.
  - قم بجمع الملفات الثابتة:
    ```bash
    docker-compose exec web python manage.py collectstatic
    ```
- **النشر:**
  - اختر خدمة استضافة تدعم Docker (مثل Railway, Render, Heroku).
  - اتبع تعليمات خدمة الاستضافة لنشر تطبيق Django Dockerized.
  - تأكد من إعداد متغيرات البيئة (DB_NAME, DB_USER, DB_PASSWORD, SECRET_KEY, GEMINI_API_KEY) على خدمة الاستضافة.

---

## 💡 نصائح إضافية للمبرمجين

- **العمل على فروع (Branches):** لا تعمل مباشرة على فرع `master` أو `develop`. أنشئ فرعاً جديداً لكل ميزة أو إصلاح (`git checkout -b feature/my-new-feature`).
- **رسائل Commit واضحة:** اكتب رسائل `commit` وصفية لما قمت به.
- **مراجعة الكود (Code Review):** راجع كود بعضكما البعض قبل دمج الفروع.
- **الراحة:** لا ترهق نفسك. خذ فترات راحة منتظمة لتجنب الإرهاق.
- **التعلم المستمر:** إذا واجهتك مشكلة، ابحث عنها. مجتمع Django و Python كبير جداً ومليء بالحلول.

بالتوفيق في رحلة التطوير!
