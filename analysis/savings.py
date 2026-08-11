"""
يربط هذا الملف بين نتيجة تحليل الاستهلاك (analysis/summary.py) وخطة التوصيات
المولّدة من الذكاء الاصطناعي (ai/advisor.py) في مخرج واحد جاهز للواجهة.
"""

from .summary import analyze_bill
from ai.advisor import generate_personalized_plan


def build_full_report(bill_data: dict, home_profile: dict) -> dict:
    """
    يأخذ بيانات الفاتورة المستخرجة من الـAI + معلومات المنزل، ويرجع تقرير كامل:
    - تحليل الاستهلاك (مقارنة بالتاريخ السابق)
    - خطة التوصيات المخصصة من AI

    home_profile مثال:
        {"members": 5, "home_type": "شقة", "has_garden": False, "has_pool": False}
    """
    consumption_analysis = analyze_bill(bill_data)

    # لو الفاتورة غير مدعومة أو فيها بيانات ناقصة، لا داعي لاستدعاء AI للنصائح
    inner = consumption_analysis.get("electricity") or consumption_analysis.get("water")
    if inner is None or inner.get("status") in ("not_electricity_bill", "not_water_bill", "missing_data"):
        return {
            "consumption_analysis": consumption_analysis,
            "advice": None,
        }

    advice = generate_personalized_plan(home_profile, consumption_analysis)

    return {
        "consumption_analysis": consumption_analysis,
        "advice": advice,
    }
