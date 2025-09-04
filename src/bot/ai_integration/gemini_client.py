"""
عميل Google Gemini AI لبوت تيليجرام تيكنو
"""
import logging
import asyncio
from typing import Optional, Dict, Any, List
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from ..config.settings import settings

logger = logging.getLogger(__name__)

class GeminiClient:
    """عميل Gemini AI"""
    
    def __init__(self, api_key: str = None):
        """تهيئة عميل Gemini AI"""
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = None
        self._initialize_client()
    
    def _initialize_client(self):
        """تهيئة عميل Gemini AI"""
        try:
            # تكوين Gemini AI
            genai.configure(api_key=self.api_key)
            
            # إنشاء نموذج Gemini
            self.model = genai.GenerativeModel(
                model_name="gemini-pro",
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                }
            )
            
            logger.info("تم تهيئة عميل Gemini AI بنجاح")
            
        except Exception as e:
            logger.error(f"خطأ في تهيئة عميل Gemini AI: {e}")
            raise
    
    async def generate_response(self, prompt: str, context: str = None) -> Optional[str]:
        """توليد رد باستخدام Gemini AI"""
        try:
            # بناء النص الكامل
            full_prompt = prompt
            if context:
                full_prompt = f"السياق: {context}\n\nالسؤال: {prompt}"
            
            # توليد الرد
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt
            )
            
            if response.text:
                return response.text.strip()
            else:
                logger.warning("لم يتم الحصول على رد من Gemini AI")
                return None
                
        except Exception as e:
            logger.error(f"خطأ في توليد الرد من Gemini AI: {e}")
            return None
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """تحليل المشاعر في النص"""
        try:
            prompt = f"""
            حلل المشاعر في النص التالي وأعطني النتيجة في شكل JSON:
            
            النص: "{text}"
            
            أريد النتيجة في هذا الشكل:
            {{
                "sentiment": "positive/negative/neutral",
                "confidence": 0.85,
                "emotions": ["joy", "anger", "sadness", "fear", "surprise"],
                "summary": "ملخص قصير للمشاعر"
            }}
            """
            
            response = await self.generate_response(prompt)
            if response:
                # محاولة تحليل JSON
                import json
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    # إذا فشل تحليل JSON، إرجاع نتيجة افتراضية
                    return {
                        "sentiment": "neutral",
                        "confidence": 0.5,
                        "emotions": [],
                        "summary": "لم يتم تحليل المشاعر بنجاح"
                    }
            
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "emotions": [],
                "summary": "فشل في تحليل المشاعر"
            }
            
        except Exception as e:
            logger.error(f"خطأ في تحليل المشاعر: {e}")
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "emotions": [],
                "summary": "خطأ في تحليل المشاعر"
            }
    
    async def summarize_conversation(self, messages: List[str], max_length: int = 200) -> Optional[str]:
        """تلخيص المحادثة"""
        try:
            # دمج الرسائل
            conversation = "\n".join(messages[-20:])  # آخر 20 رسالة
            
            prompt = f"""
            لخص المحادثة التالية في {max_length} كلمة أو أقل:
            
            المحادثة:
            {conversation}
            
            الملخص يجب أن يكون:
            - مختصر ومفيد
            - يغطي النقاط الرئيسية
            - باللغة العربية
            """
            
            response = await self.generate_response(prompt)
            return response
            
        except Exception as e:
            logger.error(f"خطأ في تلخيص المحادثة: {e}")
            return None
    
    async def detect_spam(self, text: str) -> Dict[str, Any]:
        """كشف الرسائل المزعجة"""
        try:
            prompt = f"""
            حلل النص التالي وحدد إذا كان رسالة مزعجة (spam) أم لا:
            
            النص: "{text}"
            
            أعطني النتيجة في شكل JSON:
            {{
                "is_spam": true/false,
                "confidence": 0.85,
                "reasons": ["سبب1", "سبب2"],
                "category": "advertisement/scam/repetitive/normal"
            }}
            """
            
            response = await self.generate_response(prompt)
            if response:
                import json
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    return {
                        "is_spam": False,
                        "confidence": 0.0,
                        "reasons": [],
                        "category": "normal"
                    }
            
            return {
                "is_spam": False,
                "confidence": 0.0,
                "reasons": [],
                "category": "normal"
            }
            
        except Exception as e:
            logger.error(f"خطأ في كشف الرسائل المزعجة: {e}")
            return {
                "is_spam": False,
                "confidence": 0.0,
                "reasons": [],
                "category": "normal"
            }
    
    async def generate_welcome_message(self, group_name: str, user_name: str) -> Optional[str]:
        """توليد رسالة ترحيب مخصصة"""
        try:
            prompt = f"""
            أنشئ رسالة ترحيب دافئة ومرحبة للعضو الجديد "{user_name}" في مجموعة "{group_name}".
            
            الرسالة يجب أن تكون:
            - مرحبة وودودة
            - تشجع على المشاركة
            - تذكر بقواعد المجموعة
            - لا تزيد عن 100 كلمة
            - باللغة العربية
            """
            
            response = await self.generate_response(prompt)
            return response
            
        except Exception as e:
            logger.error(f"خطأ في توليد رسالة الترحيب: {e}")
            return None
    
    async def suggest_content(self, topic: str, group_context: str = None) -> Optional[str]:
        """اقتراح محتوى ذي صلة"""
        try:
            context_info = f"\nسياق المجموعة: {group_context}" if group_context else ""
            
            prompt = f"""
            اقترح محتوى مفيد وممتع حول موضوع "{topic}".{context_info}
            
            المحتوى يجب أن يكون:
            - مفيد وتعليمي
            - مناسب للمجموعة
            - يشجع على النقاش
            - لا يزيد عن 150 كلمة
            - باللغة العربية
            """
            
            response = await self.generate_response(prompt)
            return response
            
        except Exception as e:
            logger.error(f"خطأ في اقتراح المحتوى: {e}")
            return None
    
    async def help_resolve_conflict(self, conflict_description: str) -> Optional[str]:
        """المساعدة في حل النزاعات"""
        try:
            prompt = f"""
            ساعد في حل النزاع التالي بطريقة حكيمة ومتوازنة:
            
            وصف النزاع: "{conflict_description}"
            
            اقترح حلول:
            - عادلة لجميع الأطراف
            - تحافظ على سلام المجموعة
            - عملية وقابلة للتطبيق
            - مهذبة ومحترمة
            - باللغة العربية
            """
            
            response = await self.generate_response(prompt)
            return response
            
        except Exception as e:
            logger.error(f"خطأ في المساعدة في حل النزاع: {e}")
            return None
    
    async def detect_language(self, text: str) -> Optional[str]:
        """كشف لغة النص"""
        try:
            prompt = f"""
            حدد لغة النص التالي وأعطني رمز اللغة فقط (مثل: ar, en, fr, es):
            
            النص: "{text}"
            
            أعطني رمز اللغة فقط بدون أي نص إضافي.
            """
            
            response = await self.generate_response(prompt)
            if response:
                # تنظيف الرد للحصول على رمز اللغة فقط
                language_code = response.strip().lower()
                if len(language_code) == 2:
                    return language_code
            
            return "ar"  # افتراضي
            
        except Exception as e:
            logger.error(f"خطأ في كشف اللغة: {e}")
            return "ar"
    
    async def check_profanity(self, text: str) -> Dict[str, Any]:
        """فحص الكلمات النابية"""
        try:
            prompt = f"""
            فحص النص التالي للكلمات النابية أو غير المناسبة:
            
            النص: "{text}"
            
            أعطني النتيجة في شكل JSON:
            {{
                "contains_profanity": true/false,
                "confidence": 0.85,
                "detected_words": ["كلمة1", "كلمة2"],
                "severity": "low/medium/high"
            }}
            """
            
            response = await self.generate_response(prompt)
            if response:
                import json
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    return {
                        "contains_profanity": False,
                        "confidence": 0.0,
                        "detected_words": [],
                        "severity": "low"
                    }
            
            return {
                "contains_profanity": False,
                "confidence": 0.0,
                "detected_words": [],
                "severity": "low"
            }
            
        except Exception as e:
            logger.error(f"خطأ في فحص الكلمات النابية: {e}")
            return {
                "contains_profanity": False,
                "confidence": 0.0,
                "detected_words": [],
                "severity": "low"
            }

# إنشاء مثيل عميل Gemini AI
gemini_client = GeminiClient()

