import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

print("--- Phase 2: Training the v2 Production Model (RandomForestRegressor) ---")

# 1. Load Data
try:
    data = pd.read_csv('supermarket_v2.csv')
    print(f"Loaded {len(data)} rows from supermarket_v2.csv")
except FileNotFoundError:
    print("Error: 'supermarket_v2.csv' not found.")
    print("Please run 'generate_data_v2.py' first.")
    exit()
    
# 2. Define Features (X) and Target (y)
# We drop IDs, names, and MRP (since we predict a % discount, not a final price)
X = data.drop(['Discount_Pct', 'Product_ID', 'Product_Name', 'MRP'], axis=1)
y = data['Discount_Pct']

# 3. Split Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Define Preprocessing Pipeline
# This is more advanced than Phase 1. We now SCALE numeric features.
numeric_features = [
    'Expiry_Days', 'Units_Sold_Last_Week', 'Stock_Available', 
    'Demand_Trend', 'Customer_Rating'
]
categorical_features = ['Category', 'Season']

# Create transformers
# NEW: StandardScaler scales numbers (e.g., 1-500) to a standard range (e.g., -1 to 1)
# This helps the model train better.
numeric_transformer = StandardScaler()
categorical_transformer = OneHotEncoder(handle_unknown='ignore')

# Create the preprocessor
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])

# 5. Create the Full Model Pipeline
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)) 
    # n_estimators=100 means 100 Decision Trees. n_jobs=-1 uses all your CPU cores.
])

# 6. Train the Model
print(f"Training RandomForestRegressor on {len(X_train)} samples... (This may take a minute)")
model_pipeline.fit(X_train, y_train)
print("Model training complete.")

# 7. Evaluate the Model (NEW METRICS)
print("\n--- Model Evaluation ---")
y_pred = model_pipeline.predict(X_test)

# R-squared (R2): How much of the change in discount is explained by the model?
# 1.0 is perfect. 0.90 is excellent.
r2 = r2_score(y_test, y_pred)
print(f"R-squared (R2) Score: {r2:.4f}")

# Root Mean Squared Error (RMSE): On average, how "wrong" is the model's prediction?
# A smaller number is better.
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print(f"Root Mean Squared Error (RMSE): {rmse:.4f}")
print("(A high R2 and a low RMSE mean the model is very accurate.)")


# 8. Save the Model
model_filename = 'model_v2.pkl'
joblib.dump(model_pipeline, model_filename)
print(f"\n--- ✅ Successfully saved the production 'brain' as '{model_filename}' ---")

# 9. Test with a real example
print("\n--- Example Prediction ---")

# Let's create a high-risk item:
# Meat, expiring in 2 days, low sales, high stock, off-season
sample_data = pd.DataFrame({
    'Category': ['Meat'],
    'Expiry_Days': [2],
    'Units_Sold_Last_Week': [30], # Low sales
    'Stock_Available': [450], # Very high stock
    'Demand_Trend': [0.1],   # Low demand
    'Customer_Rating': [3.1],
    'Season': ['Off']
})

predicted_discount = model_pipeline.predict(sample_data)[0]

print(f"Sample Data:\n{sample_data.to_string()}\n")
print(f"✅ Predicted Discount: {predicted_discount*100:.2f}%")
print("(This high, specific discount is exactly what we want!)")