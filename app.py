import os
import uuid
import pandas as pd
from flask import Flask, render_template, request, flash

from ai.extractor import extract_bill_data
from analysis.savings import build_full_report

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
HISTORY_CSV = os.path.join(BASE_DIR, "data", "sample_data", "consumption_history.csv")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "watter-wise-dev-secret")
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8MB حد أقصى لحجم الصورة

# لا يوجد نموذج لبيانات المنزل في الواجهة حالياً (تم تبسيطها لرفع الفاتورة فقط)
# فنستخدم ملف تعريف افتراضي عام لتوليد نصائح AI
DEFAULT_HOME_PROFILE = {
    "members": 4,
    "home_type": "منزل سكني",
    "has_garden": False,
    "has_pool": False,
}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_baseline():
    """
    قراءة آخر قيم استهلاك مسجلة (الشهر السابق) لكل من الكهرباء والمياه من البيانات
    التاريخية، لعرضها في الصفحة قبل رفع أي فاتورة.
    """
    try:
        history = pd.read_csv(HISTORY_CSV)
        return {
            "water_previous": int(history["water_liters"].iloc[-1]),
            "electricity_previous": int(history["electricity_kwh"].iloc[-1]),
        }
    except Exception:
        return {"water_previous": None, "electricity_previous": None}


@app.route("/")
def index():
    return render_template(
        "dashboard.html",
        baseline=get_baseline(),
        error=None,
        consumption_analysis=None,
        advice=None,
    )


@app.route("/analyze", methods=["POST"])
def analyze():
    baseline = get_baseline()
    file = request.files.get("bill_image")

    if file is None or file.filename == "":
        flash("يرجى اختيار صورة الفاتورة أولاً.")
        return render_template("dashboard.html", baseline=baseline, error=None,
                                consumption_analysis=None, advice=None)

    if not allowed_file(file.filename):
        flash("صيغة الملف غير مدعومة. الرجاء رفع صورة JPG أو PNG.")
        return render_template("dashboard.html", baseline=baseline, error=None,
                                consumption_analysis=None, advice=None)

    # حفظ الصورة مؤقتاً باسم فريد لتجنب تعارض الملفات
    saved_name = f"{uuid.uuid4().hex}_{file.filename}"
    saved_path = os.path.join(UPLOAD_DIR, saved_name)
    file.save(saved_path)

    try:
        # الخطوة 1: استخراج بيانات الفاتورة عبر Gemini
        bill_data = extract_bill_data(saved_path)

        if "error" in bill_data:
            return render_template("dashboard.html", baseline=baseline,
                                    error=bill_data["error"],
                                    consumption_analysis=None, advice=None)

        # الخطوة 2: تحليل الاستهلاك + توليد خطة التوصيات
        report = build_full_report(bill_data, DEFAULT_HOME_PROFILE)

        return render_template(
            "dashboard.html",
            baseline=baseline,
            error=None,
            consumption_analysis=report["consumption_analysis"],
            advice=report["advice"],
        )
    finally:
        # تنظيف الملف المؤقت بعد الانتهاء من التحليل
        if os.path.exists(saved_path):
            os.remove(saved_path)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
