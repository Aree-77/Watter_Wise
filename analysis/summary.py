from .water import load_water_history, analyze_water
from .electricity import load_electricity_history, analyze_electricity

def analyze_bill(bill_data):
    document_type = bill_data.get("document_type")

    if document_type == "water_bill":
        history = load_water_history()
        return {
            "water": analyze_water(bill_data, history)
        }

    elif document_type == "electricity_bill":
        history = load_electricity_history()
        return {
            "electricity": analyze_electricity(bill_data, history)
        }

    else:
        return {
            "status": "unsupported_document",
            "document_type": document_type,
            "message": "This document type is not currently supported for consumption analysis."
        }
