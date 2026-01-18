"""
خدمات الذكاء الاصطناعي المحدّثة
S-ACM - Smart Academic Content Management System

تم تحديث هذا الملف لـ:
1. استخدام google-generativeai SDK الرسمي بدلاً من OpenAI-compatible API
2. إضافة دعم Celery للمهام الطويلة
3. تحسين معالجة الأخطاء والـ Retry Logic
4. إضافة Caching للنتائج
"""

import os
import json
import hashlib
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from functools import wraps
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger('ai_features')

# Google Generative AI SDK
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-generativeai not installed. Run: pip install google-generativeai")

# OpenAI-compatible API (Fallback)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# PDF Processing
try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Word Processing
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# PowerPoint Processing
try:
    from pptx import Presentation
    PPTX_AVAILABLE = True
except ImportError:
    PPTX_AVAILABLE = False


def cache_ai_result(timeout: int = 3600):
    """
    Decorator لتخزين نتائج AI في الكاش
    
    Args:
        timeout: مدة التخزين بالثواني (افتراضي: ساعة)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, text: str, *args, **kwargs):
            # إنشاء مفتاح الكاش من hash النص والمعاملات
            cache_key = f"ai:{func.__name__}:{hashlib.md5(text.encode()).hexdigest()}"
            
            # محاولة الحصول من الكاش
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # تنفيذ الدالة
            result = func(self, text, *args, **kwargs)
            
            # تخزين في الكاش
            if result:
                cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator


class GeminiService:
    """
    خدمة Google Gemini للذكاء الاصطناعي
    
    تستخدم google-generativeai SDK الرسمي مع fallback إلى OpenAI-compatible API
    
    التحسينات:
    1. استخدام SDK الرسمي لأداء أفضل
    2. Retry Logic للتعامل مع الأخطاء المؤقتة
    3. Caching للنتائج المتكررة
    4. معالجة أخطاء محسّنة
    """
    
    # النماذج المتاحة
    MODELS = {
        'flash': 'gemini-2.0-flash',
        'pro': 'gemini-1.5-pro',
        'default': 'gemini-2.0-flash'
    }
    
    # الحد الأقصى لمحاولات إعادة المحاولة
    MAX_RETRIES = 3
    
    # الحد الأقصى للنص المدخل
    MAX_INPUT_LENGTH = 30000
    
    def __init__(self, model: str = 'default'):
        """
        تهيئة الخدمة
        
        Args:
            model: اسم النموذج ('flash', 'pro', 'default')
        """
        self.model_name = self.MODELS.get(model, self.MODELS['default'])
        self.client = None
        self.model = None
        self._use_native_sdk = False
        
        self._initialize_client()
    
    def _initialize_client(self):
        """تهيئة العميل"""
        api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY')
        
        # محاولة استخدام SDK الرسمي أولاً
        if GENAI_AVAILABLE and api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(self.model_name)
                self._use_native_sdk = True
                logger.info(f"Initialized Gemini with native SDK: {self.model_name}")
                return
            except Exception as e:
                logger.warning(f"Failed to initialize native SDK: {e}")
        
        # Fallback إلى OpenAI-compatible API
        if OPENAI_AVAILABLE:
            try:
                self.client = OpenAI()
                self._use_native_sdk = False
                logger.info("Initialized Gemini with OpenAI-compatible API")
                return
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
        
        logger.error("No AI client available")
    
    def is_available(self) -> bool:
        """التحقق من توفر الخدمة"""
        return self.model is not None or self.client is not None
    
    def _truncate_text(self, text: str, max_length: int = None) -> str:
        """قص النص إذا كان طويلاً جداً"""
        max_length = max_length or self.MAX_INPUT_LENGTH
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text
    
    def _generate_with_retry(self, prompt: str, system_prompt: str = None, 
                             max_tokens: int = 500, temperature: float = 0.3) -> Optional[str]:
        """
        توليد نص مع إعادة المحاولة
        
        Args:
            prompt: النص المطلوب
            system_prompt: تعليمات النظام
            max_tokens: الحد الأقصى للتوكنات
            temperature: درجة الإبداعية
            
        Returns:
            str: النص المولد أو None
        """
        import time
        
        for attempt in range(self.MAX_RETRIES):
            try:
                if self._use_native_sdk and self.model:
                    return self._generate_native(prompt, system_prompt, max_tokens, temperature)
                elif self.client:
                    return self._generate_openai(prompt, system_prompt, max_tokens, temperature)
                else:
                    return None
                    
            except Exception as e:
                logger.warning(f"AI generation attempt {attempt + 1} failed: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"AI generation failed after {self.MAX_RETRIES} attempts")
                    return None
        
        return None
    
    def _generate_native(self, prompt: str, system_prompt: str = None,
                        max_tokens: int = 500, temperature: float = 0.3) -> Optional[str]:
        """التوليد باستخدام SDK الرسمي"""
        generation_config = genai.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature
        )
        
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = self.model.generate_content(
            full_prompt,
            generation_config=generation_config
        )
        
        return response.text.strip()
    
    def _generate_openai(self, prompt: str, system_prompt: str = None,
                        max_tokens: int = 500, temperature: float = 0.3) -> Optional[str]:
        """التوليد باستخدام OpenAI-compatible API"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content.strip()
    
    # ========== استخراج النص من الملفات ==========
    
    def extract_text_from_file(self, file_obj) -> Optional[str]:
        """استخراج النص من الملف"""
        if file_obj.content_type == 'external_link':
            return None
        
        if not file_obj.local_file:
            return None
        
        file_path = Path(file_obj.local_file.path)
        extension = file_path.suffix.lower()
        
        try:
            if extension == '.pdf':
                return self._extract_from_pdf(file_path)
            elif extension == '.docx':
                return self._extract_from_docx(file_path)
            elif extension == '.pptx':
                return self._extract_from_pptx(file_path)
            elif extension in ['.txt', '.md']:
                return self._extract_from_text(file_path)
            else:
                return None
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return None
    
    def _extract_from_pdf(self, file_path: Path) -> Optional[str]:
        """استخراج النص من PDF"""
        if not PDF_AVAILABLE:
            return None
        
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    
    def _extract_from_docx(self, file_path: Path) -> Optional[str]:
        """استخراج النص من Word"""
        if not DOCX_AVAILABLE:
            return None
        
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    
    def _extract_from_pptx(self, file_path: Path) -> Optional[str]:
        """استخراج النص من PowerPoint"""
        if not PPTX_AVAILABLE:
            return None
        
        prs = Presentation(file_path)
        text = ""
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text + "\n"
        return text.strip()
    
    def _extract_from_text(self, file_path: Path) -> Optional[str]:
        """استخراج النص من ملف نصي"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    
    # ========== خدمات AI الرئيسية ==========
    
    @cache_ai_result(timeout=3600)
    def generate_summary(self, text: str, max_length: int = 500) -> str:
        """
        توليد تلخيص للنص
        
        Args:
            text: النص المطلوب تلخيصه
            max_length: الحد الأقصى لطول التلخيص
            
        Returns:
            str: التلخيص
        """
        if not self.is_available():
            return self._fallback_summary(text, max_length)
        
        text = self._truncate_text(text)
        
        system_prompt = "أنت مساعد أكاديمي متخصص في تلخيص المحتوى التعليمي باللغة العربية. قدم تلخيصات واضحة ومفيدة."
        
        prompt = f"""
قم بتلخيص النص التالي بشكل مختصر ومفيد باللغة العربية.
ركز على النقاط الرئيسية والمفاهيم الأساسية.

النص:
{text}

التلخيص:
"""
        
        result = self._generate_with_retry(prompt, system_prompt, max_length, 0.3)
        return result or self._fallback_summary(text, max_length)
    
    def _fallback_summary(self, text: str, max_length: int) -> str:
        """تلخيص بسيط في حالة عدم توفر الخدمة"""
        sentences = text.split('.')
        summary = ""
        for sentence in sentences:
            if len(summary) + len(sentence) < max_length:
                summary += sentence.strip() + ". "
            else:
                break
        return summary.strip() or text[:max_length] + "..."
    
    @cache_ai_result(timeout=3600)
    def generate_questions(self, text: str, question_type: str = 'mixed', 
                          num_questions: int = 5) -> List[Dict[str, Any]]:
        """
        توليد أسئلة من النص
        
        Args:
            text: النص المصدر
            question_type: نوع الأسئلة ('mcq', 'true_false', 'short_answer', 'mixed')
            num_questions: عدد الأسئلة
            
        Returns:
            List[Dict]: قائمة الأسئلة
        """
        if not self.is_available():
            return self._fallback_questions(text, num_questions)
        
        text = self._truncate_text(text, 8000)
        
        type_instruction = {
            'mcq': 'أسئلة اختيار من متعدد فقط',
            'true_false': 'أسئلة صح أو خطأ فقط',
            'short_answer': 'أسئلة إجابة قصيرة فقط',
            'mixed': 'مزيج من أنواع الأسئلة المختلفة'
        }.get(question_type, 'مزيج من أنواع الأسئلة')
        
        system_prompt = "أنت مدرس متخصص في إنشاء أسئلة اختبارية تعليمية باللغة العربية. قدم الإجابة بصيغة JSON فقط."
        
        prompt = f"""
قم بإنشاء {num_questions} سؤال من النص التالي.
نوع الأسئلة المطلوب: {type_instruction}

أرجع الإجابة بصيغة JSON كالتالي:
[
    {{
        "type": "mcq" أو "true_false" أو "short_answer",
        "question": "نص السؤال",
        "options": ["خيار1", "خيار2", "خيار3", "خيار4"],
        "answer": "الإجابة الصحيحة",
        "explanation": "شرح مختصر للإجابة"
    }}
]

النص:
{text}

الأسئلة (JSON فقط):
"""
        
        result = self._generate_with_retry(prompt, system_prompt, 2000, 0.5)
        
        if result:
            try:
                # محاولة استخراج JSON
                if '```json' in result:
                    result = result.split('```json')[1].split('```')[0]
                elif '```' in result:
                    result = result.split('```')[1].split('```')[0]
                
                questions = json.loads(result)
                return questions
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse questions JSON: {e}")
        
        return self._fallback_questions(text, num_questions)
    
    def _fallback_questions(self, text: str, num_questions: int) -> List[Dict[str, Any]]:
        """أسئلة بسيطة في حالة عدم توفر الخدمة"""
        return [
            {
                'type': 'short_answer',
                'question': 'ما هي الفكرة الرئيسية في هذا النص؟',
                'answer': 'راجع النص للإجابة',
                'explanation': 'هذا سؤال تلقائي'
            }
        ]
    
    def ask_document(self, text: str, question: str) -> str:
        """
        الإجابة على سؤال من سياق المستند
        
        Args:
            text: نص المستند
            question: السؤال
            
        Returns:
            str: الإجابة
        """
        if not self.is_available():
            return "عذراً، خدمة الذكاء الاصطناعي غير متاحة حالياً."
        
        text = self._truncate_text(text)
        
        system_prompt = "أنت مساعد أكاديمي يجيب على الأسئلة بناءً على محتوى المستندات المقدمة. أجب باللغة العربية بشكل واضح ومفيد."
        
        prompt = f"""
أجب على السؤال التالي بناءً على المحتوى المقدم فقط.
إذا لم تجد الإجابة في المحتوى، قل ذلك بوضوح.

المحتوى:
{text}

السؤال: {question}

الإجابة:
"""
        
        result = self._generate_with_retry(prompt, system_prompt, 500, 0.3)
        return result or "عذراً، حدث خطأ أثناء معالجة سؤالك. يرجى المحاولة مرة أخرى."


# ========== Celery Tasks (إذا كان Celery متاحاً) ==========

try:
    from celery import shared_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    # إنشاء decorator وهمي
    def shared_task(func):
        return func


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_summary_async(self, file_id: int) -> Dict[str, Any]:
    """
    مهمة Celery لتوليد التلخيص بشكل غير متزامن
    
    Args:
        file_id: معرف الملف
        
    Returns:
        Dict: نتيجة التلخيص
    """
    from apps.courses.models import LectureFile
    from apps.ai_features.models import AISummary
    
    try:
        file_obj = LectureFile.objects.get(pk=file_id)
        service = GeminiService()
        
        # استخراج النص
        text = service.extract_text_from_file(file_obj)
        if not text:
            return {'success': False, 'error': 'لا يمكن استخراج النص من الملف'}
        
        # توليد التلخيص
        summary = service.generate_summary(text)
        
        # حفظ التلخيص
        ai_summary, created = AISummary.objects.update_or_create(
            file=file_obj,
            defaults={
                'summary_text': summary,
                'is_cached': True
            }
        )
        
        return {
            'success': True,
            'summary_id': ai_summary.id,
            'summary': summary
        }
        
    except LectureFile.DoesNotExist:
        return {'success': False, 'error': 'الملف غير موجود'}
    except Exception as e:
        logger.error(f"Async summary generation failed: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_questions_async(self, file_id: int, question_type: str = 'mixed',
                            num_questions: int = 5) -> Dict[str, Any]:
    """
    مهمة Celery لتوليد الأسئلة بشكل غير متزامن
    
    Args:
        file_id: معرف الملف
        question_type: نوع الأسئلة
        num_questions: عدد الأسئلة
        
    Returns:
        Dict: نتيجة توليد الأسئلة
    """
    from apps.courses.models import LectureFile
    from apps.ai_features.models import AIGeneratedQuestion
    
    try:
        file_obj = LectureFile.objects.get(pk=file_id)
        service = GeminiService()
        
        # استخراج النص
        text = service.extract_text_from_file(file_obj)
        if not text:
            return {'success': False, 'error': 'لا يمكن استخراج النص من الملف'}
        
        # توليد الأسئلة
        questions = service.generate_questions(text, question_type, num_questions)
        
        # حفظ الأسئلة
        saved_questions = []
        for q in questions:
            ai_question = AIGeneratedQuestion.objects.create(
                file=file_obj,
                question_type=q.get('type', 'short_answer'),
                question_text=q.get('question', ''),
                options=q.get('options'),
                correct_answer=q.get('answer', ''),
                explanation=q.get('explanation', '')
            )
            saved_questions.append(ai_question.id)
        
        return {
            'success': True,
            'question_ids': saved_questions,
            'count': len(saved_questions)
        }
        
    except LectureFile.DoesNotExist:
        return {'success': False, 'error': 'الملف غير موجود'}
    except Exception as e:
        logger.error(f"Async question generation failed: {e}")
        raise self.retry(exc=e)
