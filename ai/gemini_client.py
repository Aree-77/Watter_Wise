import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# جلب مفتاح API من متغيرات البيئة للأنظمة (Environment Variables)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    # تنبيه تنفيذي ينبه الفريق عند غياب المفتاح دون أن يوقف التطبيق كلياً عند التشغيل الأول
    print("[Warning]: GEMINI_API_KEY environment variable is not set.")

# عميل واحد يُعاد استخدامه في كل الطلبات (النمط الموصى به في المكتبة الجديدة google-genai)
_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

MODEL_NAME = "gemini-3.6-flash"


def get_client() -> genai.Client:
    """
    إرجاع عميل Gemini المهيأ. يرفع خطأ واضح إذا كان المفتاح غير موجود
    بدلاً من فشل غامض لاحقاً أثناء الاستدعاء الفعلي.
    """
    if _client is None:
        raise RuntimeError(
            "GEMINI_API_KEY غير موجود. تأكد من وجود ملف .env يحتوي على المفتاح."
        )
    return _client


def build_config(system_instruction: str = None, response_mime_type: str = "application/json") -> types.GenerateContentConfig:
    """
    تجهيز إعدادات التوليد (تعليمات النظام + إعدادات التوليد) لاستخدامها مع أي طلب لموديل Gemini.

    ملاحظة: بدءاً من Gemini 3.x ألغت جوجل معاملات العينة القديمة temperature/top_p/top_k
    (تُتجاهل الآن، وستصبح خطأ HTTP 400 مستقبلاً)، والبديل الموصى به من جوجل نفسها هو
    تثبيت الدقة عبر system_instruction بدل temperature منخفضة، واستخدام thinking_level
    بدل thinking_budget.
    """
    return types.GenerateContentConfig(
        system_instruction=system_instruction,
        max_output_tokens=2048,
        response_mime_type=response_mime_type,  # يفرض على الموديل إرجاع JSON صالح مباشرة
        thinking_config=types.ThinkingConfig(thinking_level="low"),  # كافي لمهام الاستخراج والتوليد المنظم لدينا
    )
