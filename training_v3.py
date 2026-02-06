import pandas as pd
import numpy as np # <-- 1. IMPORT NUMPY
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error
import joblib

print("Starting new model training (v3)...")

# 1. Load the new dataset
try:
    data = pd.read_csv("supermarket_v3.csv")
except FileNotFoundError:
    print("Error: 'supermarket_v3.csv' not found.")
    print("Please run 'generatedata_v3.py' first to create the dataset.")
    exit()

print(f"Loaded {len(data)} samples from supermarket_v3.csv.")

# 2. Define Features (X) and Target (y)
# The AI will learn to predict Target_Discount
features = ["Category", "Days_Left", "Stock_Available", "Sales_Last_Week"]
target = "Target_Discount"

X = data[features]
y = data[target]

# 3. Create a Preprocessing Pipeline
# We must one-hot encode the 'Category'
categorical_features = ["Category"]
numeric_features = ["Days_Left", "Stock_Available", "Sales_Last_Week"]

preprocessor = ColumnTransformer(
    transformers=[
        ('num', 'passthrough', numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

# 4. Define the Model
# A RandomForestRegressor is great for learning complex, non-linear rules
model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10, min_samples_leaf=5)

# 5. Create the full pipeline
pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                           ('model', model)])

# 6. Split and Train the Model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Training the RandomForestRegressor...")
pipeline.fit(X_train, y_train)

# 7. Evaluate the Model (Optional)
print("\nEvaluating model...")
y_pred = pipeline.predict(X_test)
# --- 2. THIS IS THE FIX ---
# Calculate Mean Squared Error (MSE) first
mse = mean_squared_error(y_test, y_pred)
# Calculate Root Mean Squared Error (RMSE) by taking the square root
rmse = np.sqrt(mse) 
# --- END OF FIX ---

print(f"\nModel Training Complete. Root Mean Squared Error: {rmse:.2f}%")
print("This RMSE value shows how 'off' the model's predictions are on average.")

# 8. Save the new model
model_filename = "model_v3.pkl"
joblib.dump(pipeline, model_filename)

print(f"\n--- Successfully saved new, smarter model as '{model_filename}' ---")

