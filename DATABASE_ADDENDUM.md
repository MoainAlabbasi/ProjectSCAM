# ملحق قاعدة البيانات (Database Addendum)

هذا المستند يوثق الجداول الإضافية الموجودة في الكود الحالي والتي لم تكن مذكورة في ملف `DATABASE.md` الأصلي. هذه الجداول تمثل توسعات وتحسينات على المخطط الأساسي.

---

## الجداول الإضافية في الكود الحالي

### 1. جدول محادثات الذكاء الاصطناعي (AI_Chats)

هذا الجدول يدعم ميزة "اسأل المستند" التي تتيح للطلاب طرح أسئلة على محتوى الملفات.

| العمود (Field) | نوع البيانات (Data Type) | القيود (Constraints) | الوصف (Description) |
| :--- | :--- | :--- | :--- |
| `id` | `SERIAL` | `PRIMARY KEY` | المعرف الفريد للمحادثة. |
| `file_id` | `INT` | `FK -> Lectures_Files.file_id` | الملف المرتبط بالسؤال. |
| `user_id` | `INT` | `FK -> Users.user_id` | المستخدم الذي طرح السؤال. |
| `question` | `TEXT` | `NOT NULL` | نص السؤال. |
| `answer` | `TEXT` | `NOT NULL` | نص الإجابة من الذكاء الاصطناعي. |
| `is_helpful` | `BOOLEAN` | `NULL` | تقييم المستخدم لجودة الإجابة. |
| `created_at` | `TIMESTAMP` | `DEFAULT NOW()` | تاريخ ووقت السؤال. |
| `response_time` | `FLOAT` | `DEFAULT 0` | وقت الاستجابة بالثواني. |

---

### 2. جدول سجل استخدام الذكاء الاصطناعي (AI_Usage_Logs)

هذا الجدول يدعم نظام Rate Limiting للتحكم في عدد طلبات الذكاء الاصطناعي لكل مستخدم.

| العمود (Field) | نوع البيانات (Data Type) | القيود (Constraints) | الوصف (Description) |
| :--- | :--- | :--- | :--- |
| `id` | `SERIAL` | `PRIMARY KEY` | المعرف الفريد للسجل. |
| `user_id` | `INT` | `FK -> Users.user_id` | المستخدم الذي قام بالطلب. |
| `request_type` | `VARCHAR(20)` | `NOT NULL` | نوع الطلب (summary, questions, chat). |
| `file_id` | `INT` | `FK -> Lectures_Files.file_id` | الملف المرتبط بالطلب. |
| `tokens_used` | `INT` | `DEFAULT 0` | عدد التوكنات المستخدمة. |
| `request_time` | `TIMESTAMP` | `DEFAULT NOW()` | وقت الطلب. |
| `was_cached` | `BOOLEAN` | `DEFAULT FALSE` | هل تم استخدام الذاكرة المؤقتة. |
| `success` | `BOOLEAN` | `DEFAULT TRUE` | هل نجح الطلب. |
| `error_message` | `TEXT` | `NULL` | رسالة الخطأ إن وجدت. |

---

### 3. جدول سجل التدقيق (Audit_Logs)

هذا الجدول يسجل جميع العمليات الحساسة في النظام لأغراض الأمان والمراجعة.

| العمود (Field) | نوع البيانات (Data Type) | القيود (Constraints) | الوصف (Description) |
| :--- | :--- | :--- | :--- |
| `id` | `SERIAL` | `PRIMARY KEY` | المعرف الفريد للسجل. |
| `user_id` | `INT` | `FK -> Users.user_id` | المستخدم الذي قام بالعملية. |
| `action` | `VARCHAR(100)` | `NOT NULL` | نوع العملية. |
| `model_name` | `VARCHAR(100)` | - | اسم النموذج المتأثر. |
| `object_id` | `INT` | - | معرف الكائن المتأثر. |
| `changes` | `JSON` | - | التغييرات التي تمت. |
| `ip_address` | `VARCHAR(45)` | - | عنوان IP للمستخدم. |
| `user_agent` | `TEXT` | - | معلومات المتصفح. |
| `timestamp` | `TIMESTAMP` | `DEFAULT NOW()` | وقت العملية. |

---

### 4. جدول إعدادات النظام (System_Settings)

هذا الجدول يخزن إعدادات النظام القابلة للتعديل من لوحة التحكم.

| العمود (Field) | نوع البيانات (Data Type) | القيود (Constraints) | الوصف (Description) |
| :--- | :--- | :--- | :--- |
| `id` | `SERIAL` | `PRIMARY KEY` | المعرف الفريد للإعداد. |
| `key` | `VARCHAR(100)` | `UNIQUE, NOT NULL` | مفتاح الإعداد. |
| `value` | `TEXT` | - | قيمة الإعداد. |
| `description` | `TEXT` | - | وصف الإعداد. |
| `updated_at` | `TIMESTAMP` | `DEFAULT NOW()` | آخر تحديث. |

---

## ملاحظة

هذه الجداول الإضافية تمثل توسعات طبيعية للنظام الأساسي ولا تتعارض مع المخطط الموثق في `DATABASE.md`. يُنصح بتحديث ملف التوثيق الرسمي ليشمل هذه الجداول للحفاظ على التزامن بين الكود والتوثيق.
