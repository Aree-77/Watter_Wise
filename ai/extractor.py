import json
from PIL import Image
# استدعاء الدوال والنصوص من الملفات اللي سويناها قبل شوي
from .gemini_client import get_client, build_config, MODEL_NAME
from .prompt_templates import EXTRACTOR_SYSTEM_INSTRUCTION, EXTRACTION_PROMPT


def extract_bill_data(image_path: str) -> dict:
    """
    استخراج البيانات من صورة الفاتورة أو العداد باستخدام Gemini 2.5 Flash Multimodal.
    """
    try:
        # 1. فتح الصورة (سواء كانت من جوال المستخدم أو مرفوعة كملف)
        image = Image.open(image_path)

        # 2. تجهيز العميل وإعدادات التوليد (مع فرض إخراج JSON مباشرة)
        client = get_client()
        config = build_config(system_instruction=EXTRACTOR_SYSTEM_INSTRUCTION)

        # 3. إرسال الصورة + التعليمات للموديل (Multimodal)
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[EXTRACTION_PROMPT, image],
            config=config,
        )

        # 4. تنظيف النص المستخرج للتأكد من أنه JSON نقي بدون أي رموز إضافية (مثل ```json)
        raw_text = (response.text or "").strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]

        raw_text = raw_text.strip()

        # 5. تحويل النص إلى قاموس بايثون (Dictionary)
        extracted_data = json.loads(raw_text)
        return extracted_data

    except FileNotFoundError:
        return {"error": "لم يتم العثور على الصورة، يرجى التأكد من مسار الملف."}
    except json.JSONDecodeError:
        return {
            "error": "فشل النظام في تحويل مخرجات الذكاء الاصطناعي إلى بيانات منظمة (JSON).",
            "raw_output": raw_text if "raw_text" in locals() else None,
        }
    except Exception as e:
        return {"error": f"حدث خطأ غير متوقع أثناء تحليل الصورة: {str(e)}"}
