import pandas as pd


def load_water_history():
    return pd.read_csv("data/sample_data/consumption_history.csv")


def analyze_water(bill_data, history):
    # نتأكد أن الفاتورة فاتورة مياه
    if bill_data.get("document_type") != "water_bill":
        return {
            "status": "not_water_bill",
            "message": "The uploaded document is not a water bill."
        }

    current_consumption = bill_data.get("consumption_value")

    # إذا قيمة الاستهلاك غير موجودة
    if current_consumption is None:
        return {
            "status": "missing_data",
            "message": "Water consumption value is not available."
        }

    previous_consumption = history["water_liters"].iloc[-1]

    change_percentage = (
        (current_consumption - previous_consumption)
        / previous_consumption
    ) * 100

    return {
        "current": int(current_consumption),
        "previous": int(previous_consumption),
        "change_percentage": round(float(change_percentage), 2),
        "alert": bool(change_percentage > 20),
        "total_amount_sar": bill_data.get("total_amount_sar"),
        "invoice_date": bill_data.get("invoice_date")
    }

