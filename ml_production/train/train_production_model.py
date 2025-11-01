import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import joblib
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(script_dir)
csv_path = os.path.join(app_dir, 'public', 'dataset', 'production_plan.csv')

print(f"Loading dataset from: {csv_path}")
data = pd.read_csv(csv_path)
print(f"Dataset loaded successfully. {len(data)} records found.")

features = [
    'raw_material_available',
    'machine_availability_percent',
    'workforce_capacity_int'
]
X = data[features]
y = data['delay_reason']

model = DecisionTreeClassifier()
model.fit(X, y)
print("Model training complete.")

models_dir = os.path.join(app_dir, 'ml_models')
os.makedirs(models_dir, exist_ok=True)

model_filename = os.path.join(models_dir, 'production_delay_model.pkl')
joblib.dump(model, model_filename)
print(f"Model saved to: '{model_filename}'")

print("\n--- Model Test ---")

test_good = [[1, 100, 8]] # Assuming 8 is max capacity
pred_good = model.predict(test_good)
proba_good = model.predict_proba(test_good)
print(f"Test (Good): {pred_good[0]}")

test_bad_material = [[0, 100, 8]] # Assuming 8 is max capacity
pred_bad_mat = model.predict(test_bad_material)
proba_bad_mat = model.predict_proba(test_bad_material)
print(f"Test (Bad Material): {pred_bad_mat[0]}")

test_bad_machine = [[1, 0, 8]] # Assuming 8 is max capacity
pred_bad_mach = model.predict(test_bad_machine)
proba_bad_mach = model.predict_proba(test_bad_machine)
print(f"Test (Bad Machine): {pred_bad_mach[0]}")

# *** UPDATED TEST VALUES TO USE INTEGERS ***
test_bad_workforce = [[1, 100, 2]] # Assuming 2 is a low capacity
pred_bad_wf = model.predict(test_bad_workforce)
proba_bad_wf = model.predict_proba(test_bad_workforce)
print(f"Test (Bad Workforce): {pred_bad_wf[0]}")
