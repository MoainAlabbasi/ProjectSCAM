# ⚙️ SETUP - دليل إعداد بيئة التطوير

> **⚠️ تعليمات:** هذا الدليل مخصص لفريق التطوير (معين ومهند). اتبع الخطوات بدقة لضمان توحيد بيئة العمل.

---

## 1. المتطلبات الأساسية (Prerequisites)

يجب تثبيت البرامج التالية على نظام التشغيل **Windows** الخاص بك.

### 1.1. تفعيل WSL 2 (Windows Subsystem for Linux)

نظام WSL يسمح لك بتشغيل بيئة Linux مباشرة على Windows، وهو ضروري لتشغيل Docker بكفاءة.

- افتح PowerShell **كمسؤول (Run as Administrator)**.
- نفذ الأمر التالي لتفعيل WSL:
  ```powershell
  wsl --install
  ```
- بعد انتهاء التثبيت، أعد تشغيل جهازك.
- سيتم تثبيت توزيعة **Ubuntu** تلقائيًا. عند أول تشغيل، سيطلب منك إدخال اسم مستخدم وكلمة مرور لبيئة Linux. احفظهما جيدًا.

### 1.2. تثبيت Docker Desktop

- قم بتنزيل Docker Desktop for Windows من [الموقع الرسمي](https://www.docker.com/products/docker-desktop/).
- اتبع خطوات التثبيت. تأكد من تحديد خيار **"Use WSL 2 instead of Hyper-V"** أثناء التثبيت.
- بعد التثبيت، شغل Docker Desktop. سيقوم تلقائيًا بالارتباط مع WSL 2.

### 1.3. تثبيت VS Code

- قم بتنزيل VS Code من [الموقع الرسمي](https://code.visualstudio.com/).
- اتبع خطوات التثبيت.

### 1.4. تثبيت إضافة WSL في VS Code

- افتح VS Code.
- اذهب إلى قسم الإضافات (Extensions).
- ابحث عن `WSL` وقم بتثبيت الإضافة الرسمية من Microsoft.

---

## 2. إعداد المشروع (Project Setup)

الآن بعد أن أصبحت بيئة العمل جاهزة، سنقوم بإعداد المشروع.

### 2.1. فتح المشروع في بيئة WSL

- افتح مستكشف الملفات (File Explorer) في Windows.
- في شريط العنوان، اكتب `\wsl$` واضغط Enter. ستظهر لك مجلدات توزيعة Ubuntu.
- اذهب إلى `home` ثم اسم المستخدم الذي أنشأته.
- أنشئ مجلدًا جديدًا باسم `projects` (إذا لم يكن موجودًا).
- داخل مجلد `projects`، قم باستنساخ مستودع الكود (S-ACM-Project) بعد إنشائه.
- الآن، افتح VS Code.
- اضغط على الزر الأخضر في الزاوية السفلية اليسرى (`><`).
- اختر **"Connect to WSL"**. سيقوم VS Code بإعادة التحميل والاتصال ببيئة Linux.
- من قائمة `File`، اختر `Open Folder` وافتح مجلد المشروع الذي استنسخته.

### 2.2. بناء وتشغيل المشروع باستخدام Docker

- افتح Terminal جديد في VS Code (سيفتح تلقائيًا داخل بيئة WSL).
- تأكد من أنك داخل مجلد المشروع.
- نفذ الأوامر التالية:

  ```bash
  # 1. بناء الحاويات (يُنفذ مرة واحدة في البداية أو عند تغيير Dockerfile)
  docker-compose build

  # 2. تشغيل الحاويات في الخلفية
  docker-compose up -d

  # 3. إنشاء مشروع Django (يُنفذ مرة واحدة فقط في البداية)
  docker-compose exec web django-admin startproject acm_project .

  # 4. إنشاء تطبيق core (يُنفذ مرة واحدة فقط في البداية)
  docker-compose exec web python manage.py startapp core

  # 5. تطبيق الترحيلات الأولية (Migrations)
  docker-compose exec web python manage.py migrate

  # 6. إنشاء مستخدم مدير (Superuser)
  docker-compose exec web python manage.py createsuperuser
  ```

- بعد هذه الخطوات، يجب أن يكون المشروع يعمل. يمكنك الوصول إليه عبر المتصفح على الرابط: `http://localhost:8000`

---

## 3. أوامر Docker Compose شائعة

| الأمر | الوصف |
| :--- | :--- |
| `docker-compose up -d` | تشغيل الحاويات في الخلفية. |
| `docker-compose down` | إيقاف وحذف الحاويات. |
| `docker-compose ps` | عرض حالة الحاويات الحالية. |
| `docker-compose logs -f web` | متابعة سجلات (logs) حاوية الويب. |
| `docker-compose exec web bash` | الدخول إلى سطر الأوامر داخل حاوية الويب. |
| `docker-compose build` | إعادة بناء الحاويات بعد تغيير `Dockerfile`. |
