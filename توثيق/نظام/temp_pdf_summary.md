# ملخص المعلومات المستخرجة من ملف PDF للمشروع

## معلومات المشروع الأساسية
- **اسم المشروع:** نظام إدارة المحتوى الأكاديمي الذكي (S-ACM)
- **الهدف:** منصة ويب لإدارة المحتوى الأكاديمي في جامعة العلوم والتكنولوجيا

## أنواع المستخدمين (3 أنواع)
1. **الطالب (Student)** - المستوى الأول/الثاني/الثالث/الرابع
2. **المدرس (Teacher)** - دكتور/أستاذ مساعد
3. **المسؤول (Admin)** - رئيس قسم/مسؤول نظام

## جداول قاعدة البيانات الرئيسية

### 1. جدول المستخدمين (Users)
- user_id (PK)
- full_name
- email
- password
- role (student/teacher/admin)
- academic_id
- profile_image
- created_at
- last_login

### 2. جدول الأقسام (Departments)
- department_id (PK)
- department_name
- description

### 3. جدول التخصصات (Specializations)
- specialization_id (PK)
- specialization_name
- department_id (FK)

### 4. جدول المقررات (Courses)
- course_id (PK)
- course_name
- course_code
- description
- teacher_id (FK)
- specialization_id (FK)
- semester
- academic_year

### 5. جدول الملفات (Files)
- file_id (PK)
- file_name
- file_path
- file_type
- file_size
- course_id (FK)
- uploaded_by (FK)
- upload_date
- chapter

### 6. جدول الإشعارات (Notifications)
- notification_id (PK)
- title
- content
- notification_type
- sender_id (FK)
- course_id (FK)
- created_at
- priority
- expiry_date

### 7. جدول تسجيل المقررات (Enrollments)
- enrollment_id (PK)
- student_id (FK)
- course_id (FK)
- enrollment_date

### 8. جدول الصلاحيات (Permissions)
- permission_id (PK)
- role
- can_upload
- can_delete
- can_manage_users
- can_send_notifications

## واجهات المستخدم المصممة

### واجهات الطالب:
1. صفحة تسجيل الدخول
2. الصفحة الرئيسية (Dashboard)
3. صفحة المقررات
4. صفحة تفاصيل المقرر والملفات
5. صفحة الإشعارات
6. صفحة الجدول الدراسي
7. صفحة الملف الشخصي
8. صفحة الإعدادات

### واجهات المدرس:
1. الصفحة الرئيسية (لوحة تحكم مع إحصائيات)
2. صفحة رفع ملفات المقررات
3. صفحة رفع الإشعارات
4. صفحة الملف الشخصي
5. صفحة التقارير
6. صفحة الإعدادات

### واجهات المسؤول:
1. لوحة التحكم الرئيسية (إحصائيات شاملة)
2. إدارة المستخدمين
3. إدارة الصلاحيات
4. إدارة التخصصات
5. التقارير
6. الإعدادات

## الميزات الذكية (AI Features)
1. تلخيص المحتوى الأكاديمي تلقائياً
2. توليد أسئلة من المحتوى
3. البحث الذكي في الملفات

## التقنيات المستخدمة
- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, JavaScript, Bootstrap
- **Database:** PostgreSQL
- **AI:** Gemini API
