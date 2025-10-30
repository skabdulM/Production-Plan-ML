import frappe
import joblib
import pandas as pd
import os

def run_delay_prediction(doc, method=None):

    try:
        raw_material_available = 1
        for item in doc.mr_items:
            actual_qty = frappe.db.get_value("Bin",
                {"item_code": item.item_code, "warehouse": item.warehouse},
                "actual_qty"
            )

            if actual_qty is None or actual_qty < item.quantity:
                raw_material_available = 0
                break

        workstation_data = frappe.db.get_value("Workstation", doc.custom_workstation,
            ["custom_machine_availabilty", "production_capacity"],
            as_dict=True
        )

        if not workstation_data:
            frappe.log_error("Workstation data not found.", "Delay Prediction")
            return

        machine_avail = workstation_data.get("custom_machine_availabilty")
        workforce_cap = workstation_data.get("production_capacity")

        if machine_avail is None or workforce_cap is None:
             frappe.throw("Workstation is missing Machine Availability or Job Capacity data.")
             return

        app_path = frappe.get_app_path("ml_production")
        model_path = os.path.join(app_path, "ml_models", "production_delay_model.pkl")

        if not os.path.exists(model_path):
            frappe.throw(f"Model file not found at {model_path}", "Delay Prediction")
            return

        model = joblib.load(model_path)

        current_data = pd.DataFrame([
            [raw_material_available, machine_avail, workforce_cap]
        ], columns=[
            'raw_material_available',
            'machine_availability_percent',
            'workforce_capacity_int'
        ])

        prediction_reason = model.predict(current_data)[0]

        prediction_proba = model.predict_proba(current_data)

        probability_percent = 0

        if prediction_reason != 'No Delay':
            all_classes = list(model.classes_)
            predicted_class_index = all_classes.index(prediction_reason)
            all_probabilities = prediction_proba[0]
            delay_probability = all_probabilities[predicted_class_index]
            probability_percent = round(delay_probability * 100, 2)

        doc.custom_ai_delay_probability = probability_percent
        doc.custom_predicted_delay_reason = prediction_reason

        if probability_percent > 70:
            doc.add_tag("High Risk")
        else:
            doc.remove_tag("High Risk")

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Production Delay Prediction Failed")
