import json
from .gemini_client import get_client, build_config, MODEL_NAME
from .prompt_templates import ADVISOR_SYSTEM_INSTRUCTION, ADVISOR_PROMPT


def generate_personalized_plan(home_profile: dict, consumption_analysis: dict) -> dict:
    """
    توليد خطة التخفيض المخصصة والتوصيات بناءً على بيانات المنزل والاستهلاك باستخدام Watter-Wise.
    """
    try:
        # 1. تجهيز النص (Prompt) بدمج معلومات المنزل وتحليل الفاتورة
        # استخدام ensure_ascii=False ضروري جداً لدعم النصوص العربية وعدم تشويهها
        prompt = ADVISOR_PROMPT.format(
            home_profile=json.dumps(home_profile, ensure_ascii=False),
            consumption_analysis=json.dumps(consumption_analysis, ensure_ascii=False),
        )

        # 2. تجهيز العميل وإعدادات التوليد (Watter-Wise كمستشار استهلاك ذكي)
        client = get_client()
        config = build_config(system_instruction=ADVISOR_SYSTEM_INSTRUCTION)

        # 3. إرسال الطلب للموديل لتوليد الخطة
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=config,
        )

        # 4. تنظيف النص المستخرج لضمان أنه JSON سليم وخالي من الأكواد الزائدة
        raw_text = (response.text or "").strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]

        raw_text = raw_text.strip()

        # 5. تحويل النص إلى قاموس بايثون (Dictionary) لإرساله للواجهة
        plan_data = json.loads(raw_text)
        return plan_data

    except json.JSONDecodeError:
        # خطة طوارئ (Fallback) في حال فشل الذكاء الاصطناعي في تنسيق الـ JSON
        return {
            "analysis_summary": "تم استلام البيانات بنجاح، لكن يرجى مراجعة الاستهلاك العام للمنزل.",
            "is_abnormal_usage": False,
            "anomaly_alert": None,
            "personalized_plan": [
                {
                    "category": "عام",
                    "action": "مراجعة الأجهزة ذات الاستهلاك العالي والتأكد من إطفائها عند عدم الحاجة.",
                    "expected_financial_impact": "توفير مبدئي في الفاتورة القادمة",
                    "difficulty_level": "سهل",
                }
            ],
            "estimated_monthly_savings_sar": 0,
        }
    except Exception as e:
        return {"error": f"حدث خطأ غير متوقع أثناء توليد الخطة: {str(e)}"}
