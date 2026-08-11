from ai.extractor import extract_bill_data
from analysis.summary import analyze_bill


image_path = "data/sample_bills/electricity_bill.jpg.jpeg"

# الخطوة 1: نخلي Gemini يقرأ الفاتورة
bill_data = extract_bill_data(image_path)

print("\n--- AI OUTPUT ---")
print(bill_data)


# إذا الـAI رجع خطأ، نوقف هنا
if "error" in bill_data:
    print("\n❌ AI failed to extract the bill.")
else:
    # الخطوة 2: نرسل بيانات الـAI إلى الـAnalysis
    analysis_result = analyze_bill(bill_data)

    print("\n--- ANALYSIS OUTPUT ---")
    print(analysis_result)